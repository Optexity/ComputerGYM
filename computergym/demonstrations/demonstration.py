import json
import os

import yaml
from computergym import (
    BrowserEnvTypes,
    EnvTypes,
    Observation,
    OpenEndedWebsite,
    make_env,
)
from computergym.actions import ActionTypes, ClickAction, InputText
from computergym.envs.browser.openended_website import History
from playwright.sync_api import Locator
from pydantic import BaseModel


def read_file(file_path: str):
    with open(file_path, "r") as file:
        return file.read()


class Demonstration:
    def __init__(
        self,
        raw_html: str,
        action_type: ActionTypes,
        command: str,
        action: BaseModel,
        obs: Observation = None,
    ):

        self.raw_html: str = raw_html
        self.command: str = command
        self.action_type: ActionTypes = action_type
        self.action: BaseModel = action
        self.obs: Observation = obs

    @staticmethod
    def get_processed_data(
        env: OpenEndedWebsite, content: str, command: str, step: int
    ) -> dict:
        content, command = content.strip(), command.strip()
        print("------------")
        if "click" in command:
            action_type = ActionTypes.click
            command = command.removesuffix(".click()")
        elif "fill" in command:
            action_type = ActionTypes.input_text
            command, fill_value = command.split(".fill(")
            fill_value = fill_value.removesuffix(")")
        else:
            return

        # block all internet requests
        env.page.route("**/*", lambda route: route.abort())
        # breakpoint()
        env.page.set_content(content, wait_until="domcontentloaded", timeout=10000)

        obs = env.get_obs()

        element: Locator = eval(f"env.{command}")
        # element = env.page.locator('[data-test-id="banner-close-btn"]')
        bid = element.get_attribute("bid")
        if action_type == ActionTypes.click:
            action = ClickAction(bid=bid)
        elif action_type == ActionTypes.input_text:
            action = InputText(bid=bid, value=fill_value)
        history = History(step_number=step, obs=obs, action=action, error=None)
        history.save_history("./history")
        demonstration = Demonstration(
            raw_html=content,
            action_type=action_type,
            command=command,
            action=action,
            obs=obs,
        )
        # print(action)
        return demonstration

    @staticmethod
    def get_single_demonstration(save_dir: str, generated_code_file: str):
        env: OpenEndedWebsite = make_env(
            None,
            EnvTypes.browser,
            BrowserEnvTypes.openended,
            cache_dir=None,
            goal_message=None,
            headless=False,
        )
        _, _ = env.reset()

        generated_code_file = os.path.join(save_dir, generated_code_file)
        with open(generated_code_file, "r") as file:
            data = [line.strip() for line in file.readlines()]

        for step, line in enumerate(data):
            if "#" not in line or "uuid" not in line:
                continue
            command, sample = line.rsplit("#", 1)
            sample = json.loads(sample.strip())
            content = read_file(os.path.join(save_dir, f'{sample["uuid"]}.html'))
            # content = read_file(
            #     "/Users/sankalp/repository/github/Reinforce-Align-AI/temp.html"
            # )
            demonstration = Demonstration.get_processed_data(
                env, content, command, step
            )

    @staticmethod
    def from_yaml(yaml_file_path: str) -> list["Demonstration"]:

        SAVE_DIR = "save_dir"
        TASKS = "tasks"
        DESCRIPTION = "description"
        GENERATED_CODE = "generated_code"
        TASK_NAME = "task_name"

        with open(yaml_file_path, "r") as file:
            data = yaml.safe_load(file)

        for task in data[TASKS]:
            task_name = task[TASK_NAME]
            description = task[DESCRIPTION]
            save_dir = task[SAVE_DIR] if SAVE_DIR in task else data[SAVE_DIR]
            save_dir = os.path.join(save_dir, task_name)
            generated_code_file = (
                task[GENERATED_CODE] if GENERATED_CODE in task else data[GENERATED_CODE]
            )
            # print(f"Task Name: {task_name}")
            # print(f"Description: {description}")
            # print(f"Save Directory: {save_dir}")
            # print(f"Generated Code File: {generated_code_file}")
            # print()

            Demonstration.get_single_demonstration(save_dir, generated_code_file)

        return

        demonstrations = []
        for entry in data:
            raw_html = entry.get("raw_html")
            action_type = ActionTypes(entry.get("action_type"))
            xpath = entry.get("xpath")
            if raw_html and action_type and xpath:
                demonstration = Demonstration(raw_html, action_type, xpath)
                demonstrations.append(demonstration)
        return demonstrations


if __name__ == "__main__":
    demonstration = Demonstration.from_yaml("./dummy.yaml")
