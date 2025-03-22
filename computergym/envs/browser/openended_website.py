import copy
import logging
import os
import re
import time

import gymnasium as gym
from computergym.actions import ClickAction, InputText, TaskComplete, apply_action
from computergym.obs_processors import Observation, get_observation_from_page
from pydantic import BaseModel

import playwright.sync_api

from .history import History

logger = logging.getLogger(__name__)


class OpenEndedWebsite(gym.Env):
    def __init__(
        self,
        url: str,
        goal: str,
        cache_dir: str = None,
        preprocess_func: callable = None,
        headless: bool = False,
        proxy: str = None,
    ):
        self.url = url
        self.cache_dir = cache_dir
        self.preprocess_func = preprocess_func
        self.headless = headless
        self.proxy = proxy
        self.goal = goal
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)

        self.action_space: list[BaseModel] = [ClickAction, InputText, TaskComplete]
        self.pw = playwright.sync_api.sync_playwright().start()

        self.reset_variables()

    def render(self):
        pass

    def close(self):
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()

    def seed(self, seed=None):
        pass

    def get_action_space(self) -> list[BaseModel]:
        return self.action_space

    def reset_variables(self):
        self.current_step = 0
        self.history: list[History] = []
        self.obs = None
        self.action = None
        self.terminated = False
        self.truncated = False
        self.info = {}
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

        # important: change playwright's test id attribute from "data-testid" to "bid"
        self.pw.selectors.set_test_id_attribute("bid")
        self.browser = self.pw.chromium.launch_persistent_context(
            user_data_dir="/Users/sankalp/repository/github/Reinforce-Align-AI/browser_data",
            headless=self.headless,
            proxy={"server": self.proxy} if self.proxy else None,
        )
        self.context = self.browser
        self.context.expose_binding(
            "browsergym_page_activated",
            lambda source: self._activate_page_from_js(source["page"]),
        )

        self.page = self.context.new_page()
        if self.url:
            self.page.goto(self.url, timeout=10000)

        if self.preprocess_func:
            self.preprocess_func(self.page)

        time.sleep(5)

        self._wait_dom_loaded()
        self._active_page_check()

        self.obs = self.get_obs()
        self.info = {}

        return self.obs, self.info

    def step(self, action: BaseModel) -> tuple:
        history = History(self.current_step, self.obs, action)
        self.history.append(history)

        info = {}
        info["action_exec_start"] = time.time()
        info["action_exec_timeout"] = 0

        # try to execute the action
        logger.debug(f"Executing action")
        try:
            self.last_action = action
            self.terminated = apply_action(action, self.page)
            self.last_action_error = ""
        except Exception as e:
            logging.exception(f"Error while executing action: {action}: {e}")
            self.last_action_error = f"{type(e).__name__}: {e}"
            self.history[-1].error = self.last_action_error
            match = re.match(
                "TimeoutError: Timeout ([0-9]+)ms exceeded.", self.last_action_error
            )
            if match:
                # ms to sec
                info["action_exec_timeout"] = float(match.groups()[0]) / 1000
        history.save_history(self.cache_dir)
        # wait a bit (for the JavaScript callback to set the active page)
        time.sleep(5)  # wait for JS events to be fired (half a second)
        self.context.cookies()  # trigger all waiting Playwright callbacks on the stack (hack, see https://playwright.dev/java/docs/multithreading)

        # wait for the network to idle before extracting the observation, reward etc.
        self._wait_dom_loaded()

        # after the action is executed, the active page might have changed
        # perform a safety check
        self._active_page_check()
        logger.debug(f"Active page checked")

        # new step API wants a 5-tuple (gymnasium)
        self.obs = self.get_obs()
        reward = 0
        truncated = False
        self.current_step += 1
        return self.obs, reward, self.terminated, truncated, info

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
            # move page to the end of dictionnary
            self.page_history[page] = self.page_history.pop(page)
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
            # set last active page as the active page (most recent)
            self.page = list(self.page_history.keys())[-1]

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

    def get_obs(self):
        obs = Observation(
            goal=copy.deepcopy(self.goal),
            open_pages_urls=[page.url for page in self.context.pages],
            open_pages_titles=[page.title() for page in self.context.pages],
            active_page_index=self.context.pages.index(self.page),
            url=copy.deepcopy(self.page.url),
            last_action=copy.deepcopy(self.last_action),
            last_action_error=copy.deepcopy(self.last_action_error),
            html=None,
            axtree=None,
        )
        obs = get_observation_from_page(self.page, obs)

        return obs
