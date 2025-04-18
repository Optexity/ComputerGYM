import argparse
import json
import os
import random

import yaml
from computergym import BrowserEnvTypes, EnvTypes, OpenEndedWebsite, make_env
from computergym.actions import ClickAction, InputText, TaskComplete
from computergym.envs.browser import History
from tqdm import tqdm

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
        action_type = TaskComplete.__name__
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
        try:
            element: Locator = eval(f"env.{command}")
            bid = element.get_attribute("bid")
        except Exception as e1:
            try:
                element: Locator = eval(f"env.{command}.nth(0)")
                bid = element.get_attribute("bid")
            except Exception as e2:
                breakpoint()

    if action_type == ClickAction.__name__:
        action = ClickAction(bid=bid)
    elif action_type == InputText.__name__:
        action = InputText(bid=bid, value=fill_value)
    elif action_type == TaskComplete.__name__:
        action = TaskComplete(msg="Task completed successfully!")

    history = History(step_number=next_step, obs=obs, action=action, error=None)
    history.save_history(output_dir)
    return next_step + 1


def keep_only_last_recording_complete(processed_code_lines: list):
    # Keep only last recording_complete and remove all previous ones
    last_true_index = [i for i, a in enumerate(processed_code_lines) if a[-1]][-1]
    processed_code_lines = processed_code_lines[: last_true_index + 1]
    processed_code_lines = [a for a in processed_code_lines[:-1] if not a[-1]] + [
        processed_code_lines[-1]
    ]
    return processed_code_lines


def remove_simultaneous_click_fill(processed_code_lines: list):
    new_data = []
    for i, (command, _, _) in enumerate(processed_code_lines):
        if "click(" in command and i < len(processed_code_lines) - 1:
            command2 = processed_code_lines[i + 1][0]
            if "fill(" in command2:
                command = command.strip().removesuffix(".click()")
                command2 = command2.strip().split(".fill(")[0]
                if command != command2:
                    new_data.append(processed_code_lines[i])
            else:
                new_data.append(processed_code_lines[i])
        else:
            new_data.append(processed_code_lines[i])

    return new_data


def remove_simultaneous_fills(processed_code_lines: list):
    new_data = []
    for i, (command, _, _) in enumerate(processed_code_lines):
        if "fill(" in command and i < len(processed_code_lines) - 1:
            command2 = processed_code_lines[i + 1][0]
            if "fill(" in command2:
                command = command.strip().split(".fill(")[0]
                command2 = command2.strip().split(".fill(")[0]
                if command != command2:
                    new_data.append(processed_code_lines[i])
            else:
                new_data.append(processed_code_lines[i])
        else:
            new_data.append(processed_code_lines[i])

    return new_data


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
            processed_code_lines[-1][0] = command.strip()
        else:
            processed_code_lines.append(
                [
                    command.strip(),
                    os.path.join(record_dir, f"{code_comment['uuid']}.html"),
                    str(code_comment["recording_complete"].lower()) == "true",
                ]
            )

    next_step = 0

    processed_code_lines = keep_only_last_recording_complete(processed_code_lines)
    processed_code_lines = remove_simultaneous_click_fill(processed_code_lines)
    processed_code_lines = remove_simultaneous_fills(processed_code_lines)

    for command, content_path, recording_complete in processed_code_lines:
        next_step = get_processed_data(
            env, content_path, command, next_step, output_dir, recording_complete
        )


def from_yaml(yaml_file_path: str, seed: int):

    env: OpenEndedWebsite = make_env(
        None,
        EnvTypes.browser,
        BrowserEnvTypes.openended,
        cache_dir=None,
        goal_message=None,
        headless=True,
    )
    _, _ = env.reset()

    for _ in range(seed):
        _ = env.get_obs()

    with open(yaml_file_path, "r") as file:
        data = yaml.safe_load(file)

    random.seed(seed)
    random.shuffle(data[TASKS])
    for task in tqdm(data[TASKS]):
        task_name = task[TASK_NAME]
        record_dir = os.path.join(data[SAVE_DIR], task_name, data[RECORDER_DIR])
        output_dir = os.path.join(
            data[SAVE_DIR], task_name, data[PROCESSED_OUTPUT_DIR], f"seed-{seed}"
        )
        code_file = os.path.join(data[SAVE_DIR], task_name, data[GENERATED_CODE])
        os.makedirs(output_dir, exist_ok=True)
        get_single_demonstration(env, record_dir, code_file, output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process YAML file.")
    parser.add_argument("--yaml", type=str)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    demonstration = from_yaml(args.yaml, args.seed)
