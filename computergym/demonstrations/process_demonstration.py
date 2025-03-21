import argparse
import json
import os

import yaml
from computergym import BrowserEnvTypes, EnvTypes, OpenEndedWebsite, make_env
from computergym.actions import ClickAction, InputText, TaskComplete
from computergym.envs.browser import History

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
    recording_complete: bool,
) -> int:
    command = command.strip()
    if recording_complete:
        action = TaskComplete()
    elif ".click(" in command:
        action_type = ClickAction.__name__
        command = command.removesuffix(".click()")
    elif ".fill(" in command:
        action_type = InputText.__name__
        command, fill_value = command.split('.fill("')
        fill_value = fill_value.removesuffix('")')
    else:
        return next_step

    content = read_file(content_path)

    # block all internet requests
    env.page.route("**/*", lambda route: route.abort())
    env.page.set_content(content, wait_until="domcontentloaded", timeout=10000)

    obs = env.get_obs()
    if not recording_complete:
        element: Locator = eval(f"env.{command}")
        try:
            bid = element.get_attribute("bid")
        except Exception as e:
            breakpoint()

    if action_type == ClickAction.__name__:
        action = ClickAction(bid=bid)
    elif action_type == InputText.__name__:
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
                [
                    command,
                    os.path.join(record_dir, f"{code_comment['uuid']}.html"),
                    str(code_comment["recording_complete"].lower()) == "true",
                ]
            )

    next_step = 0
    recording_complete_seen = False
    for command, content_path, recording_complete in processed_code_lines:
        recording_complete_seen = recording_complete_seen or recording_complete
        next_step = get_processed_data(
            env,
            content_path,
            command,
            next_step,
            output_dir,
            recording_complete and not recording_complete_seen,
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
        record_dir = os.path.join(data[SAVE_DIR], task_name, data[RECORDER_DIR])
        output_dir = os.path.join(data[SAVE_DIR], task_name, data[PROCESSED_OUTPUT_DIR])
        code_file = os.path.join(data[SAVE_DIR], task_name, data[GENERATED_CODE])
        os.makedirs(output_dir, exist_ok=True)
        get_single_demonstration(env, record_dir, code_file, output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process YAML file.")
    parser.add_argument("--yaml", type=str)
    args = parser.parse_args()
    demonstration = from_yaml(args.yaml)
