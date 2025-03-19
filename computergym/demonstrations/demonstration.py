import json
import os

import yaml
from computergym import BrowserEnvTypes, EnvTypes, OpenEndedWebsite, make_env
from computergym.actions import ActionTypes, ClickAction, InputText
from computergym.envs.browser.openended_website import History
from playwright.sync_api import Locator

SAVE_DIR = "save_dir"
GENERATED_CODE = "generated_code"
TASKS = "tasks"
TASK_NAME = "task_name"
DESCRIPTION = "description"
URL = "url"
RECORDER_DIR = "recorder_dir"
PROCESSED_OUTPUT_DIR = "processed_output_dir"


def read_file(file_path: str):
    with open(file_path, "r") as file:
        return file.read()


def get_processed_data(
    env: OpenEndedWebsite,
    content_path: str,
    command: str,
    next_step: int,
    output_dir: str,
) -> int:
    command = command.strip()
    if "click" in command:
        action_type = ActionTypes.click
        command = command.removesuffix(".click()")
    elif "fill" in command:
        action_type = ActionTypes.input_text
        command, fill_value = command.split('.fill("')
        fill_value = fill_value.removesuffix('")')
    else:
        return next_step

    content = read_file(content_path)

    # block all internet requests
    env.page.route("**/*", lambda route: route.abort())
    env.page.set_content(content, wait_until="domcontentloaded", timeout=10000)

    obs = env.get_obs()
    element: Locator = eval(f"env.{command}")
    bid = element.get_attribute("bid")
    if action_type == ActionTypes.click:
        action = ClickAction(bid=bid)
    elif action_type == ActionTypes.input_text:
        action = InputText(bid=bid, value=fill_value)
    history = History(step_number=next_step, obs=obs, action=action, error=None)
    history.save_history(output_dir)
    return next_step + 1


def get_single_demonstration(
    env: OpenEndedWebsite, record_dir: str, code_file: str, output_dir: str
):

    with open(code_file, "r") as file:
        data = [line.strip() for line in file.readlines()]

    processed_code_lines = []
    for line in data:
        if "#" not in line or "uuid" not in line:
            continue
        command, code_comment = line.rsplit("#", 1)
        code_comment = json.loads(code_comment.strip())
        if (
            str(code_comment["merge_with_previous"].lower()) == "true"
            and "page.goto" not in command
        ):
            processed_code_lines[-1][0] = command
        else:
            processed_code_lines.append(
                [command, os.path.join(record_dir, f"{code_comment['uuid']}.html")]
            )

    next_step = 0
    for command, content_path in processed_code_lines:
        next_step = get_processed_data(
            env, content_path, command, next_step, output_dir
        )


def from_yaml(yaml_file_path: str):

    with open(yaml_file_path, "r") as file:
        data = yaml.safe_load(file)

    env: OpenEndedWebsite = make_env(
        None,
        EnvTypes.browser,
        BrowserEnvTypes.openended,
        cache_dir=None,
        goal_message=None,
        headless=True,
    )
    _, _ = env.reset()

    for task in data[TASKS]:
        task_name = task[TASK_NAME]
        description = task[DESCRIPTION]
        record_dir = os.path.join(data[SAVE_DIR], task_name, data[RECORDER_DIR])
        output_dir = os.path.join(data[SAVE_DIR], task_name, data[PROCESSED_OUTPUT_DIR])
        code_file = os.path.join(data[SAVE_DIR], task_name, data[GENERATED_CODE])
        os.makedirs(output_dir, exist_ok=True)
        get_single_demonstration(env, record_dir, code_file, output_dir)


if __name__ == "__main__":
    demonstration = from_yaml("./dummy.yaml")
