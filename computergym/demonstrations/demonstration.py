import json

from computergym import (
    BrowserEnvTypes,
    EnvTypes,
    Observation,
    OpenEndedWebsite,
    make_env,
)
from computergym.actions import ActionTypes
from pydantic import BaseModel


class Demonstration:
    def __init__(
        self,
        raw_html: str,
        action_type: ActionTypes,
        xpath: str,
        action: BaseModel,
        obs: Observation = None,
    ):

        self.raw_html = raw_html
        self.xpath = xpath
        self.action_type = action_type
        self.action = action
        self.obs = obs

    @staticmethod
    def from_json(file_path: str) -> list["Demonstration"]:

        with open(file_path, "r") as file:
            data = json.load(file)
        demonstrations = []
        for entry in data:
            raw_html = entry.get("raw_html")
            action_type = ActionTypes(entry.get("action_type"))
            xpath = entry.get("xpath")
            if raw_html and action_type and xpath:
                demonstration = Demonstration(raw_html, action_type, xpath)
                demonstrations.append(demonstration)
        return demonstrations

    def get_processed_data(self) -> dict:
        env: OpenEndedWebsite = make_env(
            None,
            EnvTypes.browser,
            BrowserEnvTypes.openended,
            cache_dir=None,
            goal_message=None,
            headless=True,
        )
        env.page.route(
            "**/*", lambda route: route.abort()
        )  # block all internet requests
        env.page.set_content(
            self.raw_html, wait_until="domcontentloaded", timeout=10000
        )
        self.obs = env.get_obs()
        if self.xpath:
            element = env.page.locator(f"xpath={self.xpath}").first
            self.action.bid = element.get_attribute("bid")
        env.close()
