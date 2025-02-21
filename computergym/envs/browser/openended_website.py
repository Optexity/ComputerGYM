import copy
import logging
import re
import time

import browsergym.core
import gymnasium as gym
import numpy as np
import playwright.sync_api
from computergym.actions import Action, ActionTypes
from computergym.envs.browser import _get_global_playwright
from computergym.obs_processors import (
    ObsProcessorTypes,
    axtree_processor,
    html_processor,
    screenshot_processor,
    som_processor,
)
from computergym.obs_processors.observations import (
    MarkingError,
    _post_extract,
    _pre_extract,
    extract_dom_extra_properties,
    extract_dom_snapshot,
    extract_merged_axtree,
    extract_screenshot,
)
from PIL import Image

logger = logging.getLogger(__name__)


# Convert numpy array to PIL Image and save
def save_screenshot(screenshot_array, filename="screenshot.png"):
    if isinstance(screenshot_array, np.ndarray):
        img = Image.fromarray(screenshot_array)
        img.save(filename)


class OpenEndedWebsite(gym.Env):
    def __init__(self, url: str, obs_processors: list[ObsProcessorTypes]):
        self.url = url
        self.obs_processors = obs_processors
        self.history = []
        self.obs = {}
        self.action = None
        self.terminated = False
        self.truncated = False
        self.info = {}

        self.action_space = [
            ActionTypes.click,
            ActionTypes.input_text,
            ActionTypes.scroll,
        ]

        ## TODO: remove this when we implement our own environment
        self.env = gym.make(
            "browsergym/openended",
            task_kwargs={"start_url": url},  # starting URL
            wait_for_user_message=True,  # wait for a user message after each agent message sent to the chat
            headless=False,  # run the browser in headless mode
        )

        # playwright
        self.browser: playwright.sync_api.Browser = None
        self.context: playwright.sync_api.BrowserContext = None
        self.page: playwright.sync_api.Page = None
        self.page_history: dict = {}

    def format_obs(self, obs):
        temp = {
            "chat_messages": obs["chat_messages"],
            "screenshot": obs["screenshot"],
            "goal_object": obs["goal_object"],
            "last_action": obs["last_action"],
            "last_action_error": obs["last_action_error"],
            "open_pages_urls": obs["open_pages_urls"],
            "open_pages_titles": obs["open_pages_titles"],
            "active_page_index": obs["active_page_index"],
        }

        for processor in self.obs_processors:
            if processor == ObsProcessorTypes.html:
                temp[processor] = html_processor(obs["dom_object"])
            elif processor == ObsProcessorTypes.axtree:
                temp[processor] = axtree_processor(obs["axtree_object"])
            elif processor == ObsProcessorTypes.screenshot:
                temp[processor] = screenshot_processor(obs["screenshot"])
                save_screenshot(temp[processor], "screenshot.png")
            elif processor == ObsProcessorTypes.som:
                temp[processor] = som_processor(
                    obs["screenshot"], obs["extra_element_properties"]
                )
                save_screenshot(temp[processor], "som.png")
            else:
                print(f"Warning: ObsProcessor {processor} not implemented. Skipping.")
        return temp

    def reset(self):
        ## TODO: remove self.env when we implement our own environment
        obs, info = self.env.reset()
        self.obs = self.format_obs(obs)
        return self.obs, info

    def get_browser_gym_action(
        self, action_type: ActionTypes, action_params: list[str | int]
    ):
        ## TODO: this currently is to handle browsergym actions
        if action_type == ActionTypes.click:
            new_params = [f'"{param}"' for param in action_params]
            return f"""```{action_type.value}({','.join(new_params)})```"""
        elif action_type == ActionTypes.input_text:
            new_params = [f'"{param}"' for param in action_params]
            return f"""```fill({','.join(new_params)})```"""
        elif action_type == ActionTypes.scroll:
            # For scroll, convert params to int and don't add quotes
            new_params = [str(int(param)) for param in action_params]
            return f"""```scroll({','.join(new_params)})```"""

        raise ValueError(
            f"Invalid action type: {action_type}. Supported types are: {self.action_space}"
        )

    def step(self, action_type: ActionTypes, action_params: list[str]):
        ## TODO: remove self.env when we implement our own environment
        action = self.get_browser_gym_action(action_type, action_params)
        obs, reward, terminated, truncated, info = self.env.step(action)
        self.obs = self.format_obs(obs)
        return self.obs, reward, terminated, truncated, info
        self.obs = {}
        self.main_observation = {}
        for processor in self.obs_processors:
            self.obs[processor] = self.obs_processors[processor](self.main_observation)
        return self.obs

    def render(self):
        pass

    def close(self):
        ## TODO: remove this when we implement our own environment
        self.env.close()

    def seed(self, seed=None):
        pass

    def get_action_space(self) -> list[ActionTypes]:
        return self.action_space

    def get_observation_space(self) -> list[ObsProcessorTypes]:
        pass

    def _wait_dom_loaded(self):
        for page in self.context.pages:
            try:
                page.wait_for_load_state("domcontentloaded", timeout=3000)
            except playwright.sync_api.Error:
                pass
            for frame in page.frames:
                try:
                    frame.wait_for_load_state("domcontentloaded", timeout=3000)
                except playwright.sync_api.Error:
                    pass

    def _activate_page_from_js(self, page: playwright.sync_api.Page):
        logger.debug(f"_activate_page_from_js(page) called, page={str(page)}")
        if not page.context == self.context:
            raise RuntimeError(
                f"Unexpected: activating a page that belongs to a different browser context ({page})."
            )

        # add the activated page to the page history (or move it to last which is the most recent)
        if page in self.page_history:
            self.page_history[page] = self.page_history.pop(
                page
            )  # move page to the end of dictionnary
        else:
            self.page_history[page] = None  # add page to the end of dictionnary

        self.page = page

    def _active_page_check(self):
        # make sure there is always a page open
        # if all pages have been closed, create a new page
        if len(self.context.pages) == 0:
            logger.warning(f"All pages are closed, opening a new page.")
            self.page = self.context.new_page()

        # if the active page got closed, get the last active page from the history
        while self.page_history and (
            self.page.is_closed() or self.page not in self.context.pages
        ):
            self.page_history.pop(self.page)  # remove active page from history
            self.page = list(self.page_history.keys())[
                -1
            ]  # set last active page as the active page (most recent)

        # active page should share the same browser context with the environment
        if self.page not in self.context.pages:
            raise RuntimeError(
                f"Unexpected: active page is not part of the browser context's open pages ({self.page})."
            )

        # active page should not be closed
        if self.page.is_closed():
            raise RuntimeError(
                f"Unexpected: active page has been closed ({self.page})."
            )

    def _get_obs(self):
        # for retries_left in reversed(range(EXTRACT_OBS_MAX_TRIES)):
        try:
            # pre-extraction, mark dom elements (set bid, set dynamic attributes like value and checked)
            _pre_extract(
                self.page,
                tags_to_mark="all",
                lenient=True,
            )

            dom = extract_dom_snapshot(self.page)
            axtree = extract_merged_axtree(self.page)
            extra_properties = extract_dom_extra_properties(dom)
        except (playwright.sync_api.Error, MarkingError) as e:
            err_msg = str(e)
            # try to add robustness to async events (detached / deleted frames)
            raise e
            # break

        # post-extraction cleanup of temporary info in dom
        _post_extract(self.page)

        # obs is generic to all tasks
        obs = {
            "chat_messages": tuple(copy.deepcopy(self.chat.messages)),
            "goal_object": tuple(
                copy.deepcopy(self.goal_object)
            ),  # new goal format, list of messages openai style
            "open_pages_urls": tuple(page.url for page in self.context.pages),
            "open_pages_titles": tuple(page.title() for page in self.context.pages),
            "active_page_index": np.asarray([self.context.pages.index(self.page)]),
            "url": self.page.url,  # redundant with "open_pages_urls" and "active_page_index"
            "screenshot": extract_screenshot(self.page),
            "dom_object": dom,
            "axtree_object": axtree,
            "extra_element_properties": extra_properties,
            "last_action": self.last_action,
            "last_action_error": self.last_action_error,
            "elapsed_time": np.asarray([time.time() - self.start_time]),
        }

        return obs

    def reset(self, seed=None):
        self.browser = _get_global_playwright().chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.context.expose_binding(
            "browsergym_page_activated",
            lambda source: self._activate_page_from_js(source["page"]),
        )
        self.page = self.context.new_page()
        self._wait_dom_loaded()
        self._active_page_check()
        obs = self._get_obs()
        obs = self.format_obs(obs)
        info = {}
        return obs, info

    def step(self, action: Action) -> tuple:

        # self.last_action = action

        info = {}
        info["action_exec_start"] = time.time()
        info["action_exec_timeout"] = 0

        # def send_message_to_user(text: str):
        #     if not isinstance(text, str):
        #         raise ValueError(f"Forbidden value: {text} is not a string")
        #     self.chat.add_message(role="assistant", msg=text)

        # def report_infeasible_instructions(reason: str):
        #     if not isinstance(reason, str):
        #         raise ValueError(f"Forbidden value: {reason} is not a string")
        #     self.chat.add_message(role="infeasible", msg=reason)
        #     self.infeasible_message_received = True

        # try to execute the action
        logger.debug(f"Executing action")
        try:
            # if self.action_mapping:
            #     code = self.action_mapping(action)
            # else:
            #     code = action
            # execute_python_code(
            #     code,
            #     self.page,
            #     send_message_to_user=send_message_to_user,
            #     report_infeasible_instructions=report_infeasible_instructions,
            # )

            # TODO: implement action execution

            self.last_action_error = ""
        except Exception as e:
            self.last_action_error = f"{type(e).__name__}: {e}"
            match = re.match(
                "TimeoutError: Timeout ([0-9]+)ms exceeded.", self.last_action_error
            )
            if match:
                info["action_exec_timeout"] = (
                    float(match.groups()[0]) / 1000
                )  # ms to sec
        logger.debug(f"Action executed")
        info["action_exec_stop"] = time.time()

        # wait a bit (for the JavaScript callback to set the active page)
        time.sleep(0.5)  # wait for JS events to be fired (half a second)
        self.context.cookies()  # trigger all waiting Playwright callbacks on the stack (hack, see https://playwright.dev/java/docs/multithreading)

        # wait for the network to idle before extracting the observation, reward etc.
        self._wait_dom_loaded()

        # after the action is executed, the active page might have changed
        # perform a safety check
        self._active_page_check()
        logger.debug(f"Active page checked")

        # new step API wants a 5-tuple (gymnasium)
        obs = self._get_obs()
        obs = self.format_obs(obs)
        reward = 0
        terminated = False
        truncated = False

        return obs, reward, terminated, truncated, info
