import json
import os

from computergym.actions import string_to_action_type
from computergym.obs_processors import Observation
from computergym.utils import read_file, save_screenshot, save_str_to_file
from pydantic import BaseModel


def get_action_string(action: BaseModel):
    string = action.model_dump()
    string["action"] = action.__class__.__name__
    string = json.dumps(string, indent=4)
    return string


def parse_action_string(string) -> BaseModel:
    string: dict = json.loads(string)
    action_class_string = string.pop("action")
    action_class = string_to_action_type[action_class_string]
    action = action_class.model_validate(string)
    return action


class History:
    def __init__(
        self,
        step_number: int,
        obs: Observation,
        action: BaseModel,
        error: str = None,
    ):
        self.step_number = step_number
        self.obs = obs
        self.action = action
        self.error = error

    def save_history(self, cache_dir: str):
        if cache_dir:
            cache_dir = os.path.join(cache_dir, f"step-{self.step_number}")
            os.makedirs(cache_dir, exist_ok=True)

        if self.obs.html is not None:
            save_str_to_file(self.obs.html, cache_dir, f"html-{self.step_number}.txt")
        if self.obs.axtree is not None:
            save_str_to_file(
                self.obs.axtree, cache_dir, f"axtree-{self.step_number}.txt"
            )
        if self.obs.screenshot is not None:
            save_screenshot(
                self.obs.screenshot, cache_dir, f"screenshot-{self.step_number}.png"
            )
        if self.obs.som is not None:
            save_screenshot(self.obs.som, cache_dir, f"som-{self.step_number}.png")

        string = get_action_string(self.action)
        save_str_to_file(string, cache_dir, f"action-{self.step_number}.txt")

        if self.error is not None:
            save_str_to_file(self.error, cache_dir, f"error-{self.step_number}.txt")

    @staticmethod
    def read_history(cache_dir: str) -> list["History"]:
        history = []
        all_steps = [
            int(a.removeprefix("step-"))
            for a in os.listdir(cache_dir)
            if a.startswith("step-")
        ]
        for step_number in sorted(all_steps):
            step_dir = os.path.join(cache_dir, f"step-{step_number}")
            obs = Observation(
                goal=None,
                open_pages_urls=None,
                open_pages_titles=None,
                active_page_index=None,
                url=None,
                last_action=None,
                last_action_error=None,
                html=read_file(os.path.join(step_dir, f"html-{step_number}.txt")),
                axtree=read_file(os.path.join(step_dir, f"axtree-{step_number}.txt")),
            )

            string = read_file(os.path.join(step_dir, f"action-{step_number}.txt"))
            action = parse_action_string(string)
            history.append(History(step_number=step_number, obs=obs, action=action))

        return history
