import copy
import json
import logging
import os
import re
import time

import gymnasium as gym
import numpy as np
import playwright.sync_api
from computergym.actions import ActionTypes
from computergym.actions.action import ActionTypes
from computergym.actions.action_utils import apply_action
from computergym.actions.functions import *
from computergym.chats.chat import Chat
from computergym.envs.browser import _get_global_playwright
from computergym.obs_processors import ObsProcessorTypes
from computergym.obs_processors.observations import (
    MarkingError,
    _post_extract,
    _pre_extract,
    extract_dom_extra_properties,
    extract_dom_snapshot,
    extract_merged_axtree,
    extract_screenshot,
)
from computergym.obs_processors.utils import format_obs
from computergym.utils import save_screenshot, save_str_obs
from pydantic import BaseModel

logger = logging.getLogger(__name__)
EXTRACT_OBS_MAX_TRIES = 5


class History:
    def __init__(
        self,
        step_number: int,
        obs: dict,
        action: BaseModel,
    ):
        self.step_number = step_number
        self.obs = obs
        self.action = action

    def save_history(self, cache_dir: str):
        if cache_dir:
            cache_dir = os.path.join(cache_dir, f"step-{self.step_number}")
            os.makedirs(cache_dir, exist_ok=True)

        for processor, value in self.obs.items():
            if processor == ObsProcessorTypes.html:
                save_str_obs(value, cache_dir, f"html-{self.step_number}.txt")
            elif processor == ObsProcessorTypes.axtree:
                save_str_obs(value, cache_dir, f"axtree-{self.step_number}.txt")
            elif processor == ObsProcessorTypes.screenshot:
                save_screenshot(value, cache_dir, f"screenshot-{self.step_number}.png")
            elif processor == ObsProcessorTypes.som:
                save_screenshot(value, cache_dir, f"som-{self.step_number}.png")

        string = self.action.model_dump()
        string["action"] = self.action.__class__.__name__
        string = json.dumps(string, indent=4)
        save_str_obs(string, cache_dir, f"action-{self.step_number}.txt")


class OpenEndedWebsite(gym.Env):
    def __init__(
        self,
        url: str,
        obs_processors: list[ObsProcessorTypes],
        cache_dir: str = None,
        preprocess_func: callable = None,
    ):
        self.url = url
        self.obs_processors = obs_processors
        self.cache_dir = cache_dir
        self.preprocess_func = preprocess_func
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)

        self.action_space = [
            ActionTypes.click,
            ActionTypes.input_text,
            ActionTypes.scroll_up,
            ActionTypes.scroll_down,
            ActionTypes.scroll_left,
            ActionTypes.scroll_right,
            ActionTypes.select_option,
            ActionTypes.check,
            ActionTypes.uncheck,
            ActionTypes.hover,
            ActionTypes.noop,
            ActionTypes.task_complete,
        ]

        self.reset_variables()

    def render(self):
        pass

    def close(self):
        if self.chat:
            self.chat.close()
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()

    def seed(self, seed=None):
        pass

    def get_action_space(self) -> list[ActionTypes]:
        return self.action_space

    def get_observation_space(self) -> list[ObsProcessorTypes]:
        pass

    def reset_variables(self):
        self.current_step = 0
        self.history: list[History] = []
        self.obs = None
        self.action = None
        self.terminated = False
        self.truncated = False
        self.info = {}
        self.infeasible_message_received = False
        self.chat: Chat = None
        self.goal_object = None
        self.last_action = None
        self.last_action_error = None

        # playwright
        self.browser: playwright.sync_api.Browser = None
        self.context: playwright.sync_api.BrowserContext = None
        self.page: playwright.sync_api.Page = None
        self.page_history: dict = {}

    def reset(self):

        self.reset_variables()
        self.close()

        pw: playwright.sync_api.Playwright = _get_global_playwright()
        # important: change playwright's test id attribute from "data-testid" to "bid"
        pw.selectors.set_test_id_attribute("bid")
        self.browser = pw.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.context.expose_binding(
            "browsergym_page_activated",
            lambda source: self._activate_page_from_js(source["page"]),
        )

        # create the chat
        self.chat = Chat(headless=False, chat_size=(500, 800), record_video_dir=None)

        self.page = self.context.new_page()
        self.page.goto(self.url, timeout=10000)

        # initialize the chat
        self.chat.add_message(
            role="assistant",
            msg="Hi! I am your UI assistant, I can perform web tasks for you. What can I help you with?",
        )

        if self.preprocess_func:
            self.preprocess_func(self.page, self.chat)

        time.sleep(10)

        self._wait_dom_loaded()
        self._active_page_check()

        self.infeasible_message_received = False

        self._wait_for_user_message()
        self.goal_object = self.chat.messages[-1]["message"]
        obs = self._get_obs()
        self.obs = format_obs(obs, self.obs_processors)
        self.info = {}

        return self.obs, self.info

    def step(self, action: BaseModel) -> tuple:
        history = History(self.current_step, self.obs, action)
        self.history.append(history)
        history.save_history(self.cache_dir)

        info = {}
        info["action_exec_start"] = time.time()
        info["action_exec_timeout"] = 0

        # try to execute the action
        logger.debug(f"Executing action")
        try:
            self.last_action = action
            apply_action(
                action,
                self.page,
                send_message_to_user=self.send_message_to_user,
                report_infeasible_instructions=self.report_infeasible_instructions,
                send_task_complete=self.send_task_complete,
            )

            self.last_action_error = ""
        except Exception as e:
            logging.exception(f"Error while executing action: {action}: {e}")
            self.last_action_error = f"{type(e).__name__}: {e}"
            match = re.match(
                "TimeoutError: Timeout ([0-9]+)ms exceeded.", self.last_action_error
            )
            if match:
                info["action_exec_timeout"] = (
                    float(match.groups()[0]) / 1000
                )  # ms to sec

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
        self.obs = format_obs(obs, self.obs_processors)
        reward = 0
        done = (
            self.chat.messages[-1]["role"] == "user"
            and self.chat.messages[-1]["message"] == "exit"
        )
        terminated = done or (
            self.infeasible_message_received or self.terminated
        )  # task or agent can terminate the episode
        truncated = False
        self.current_step += 1
        return self.obs, reward, terminated, truncated, info

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

    def _wait_for_user_message(self):
        # if last message is from the assistant, wait for a user message to continue
        if self.chat.messages[-1]["role"] == "assistant":
            self.chat.wait_for_user_message()

    def _get_obs(self):
        for retries_left in reversed(range(EXTRACT_OBS_MAX_TRIES)):
            try:
                # pre-extraction, mark dom elements (set bid, set dynamic attributes like value and checked)
                _pre_extract(
                    self.page,
                )

                dom = extract_dom_snapshot(self.page)
                axtree = extract_merged_axtree(self.page)
                extra_properties = extract_dom_extra_properties(dom)
            except (playwright.sync_api.Error, MarkingError) as e:
                err_msg = str(e)
                # try to add robustness to async events (detached / deleted frames)
                if retries_left > 0 and (
                    "Frame was detached" in err_msg
                    or "Frame with the given frameId is not found" in err_msg
                    or "Execution context was destroyed" in err_msg
                    or "Frame has been detached" in err_msg
                    or "Cannot mark a child frame without a bid" in err_msg
                    or "Cannot read properties of undefined" in err_msg
                ):
                    logger.warning(
                        f"An error occurred while extracting the dom and axtree. Retrying ({retries_left}/{EXTRACT_OBS_MAX_TRIES} tries left).\n{repr(e)}"
                    )
                    # post-extract cleanup (ARIA attributes)
                    _post_extract(self.page)
                    time.sleep(0.5)
                    continue
                else:
                    raise e
            break

        # post-extraction cleanup of temporary info in dom
        _post_extract(self.page)

        # obs is generic to all tasks
        obs = {
            "chat_messages": tuple(copy.deepcopy(self.chat.messages)),
            "goal_object": self.goal_object,
            # "goal_object": tuple(
            #     copy.deepcopy(self.goal_object)
            # ),  # new goal format, list of messages openai style
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
        }

        return obs

    def send_message_to_user(self, text: str):
        if not isinstance(text, str):
            raise ValueError(f"Forbidden value: {text} is not a string")
        self.chat.add_message(role="assistant", msg=text)

    def report_infeasible_instructions(self, reason: str):
        if not isinstance(reason, str):
            raise ValueError(f"Forbidden value: {reason} is not a string")
        self.chat.add_message(role="infeasible", msg=reason)
        self.infeasible_message_received = True

    def send_task_complete(self, msg: str = "I'm done!"):
        if not isinstance(msg, str):
            raise ValueError(f"Forbidden value: {msg} is not a string")
        self.chat.add_message(role="assistant", msg=msg)
        self.terminated = True
