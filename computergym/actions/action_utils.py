import json

from pydantic import BaseModel

from .action import (
    ActionTypes,
    Check,
    ClickAction,
    Hover,
    InputText,
    Noop,
    ScrollDownAction,
    ScrollLeftAction,
    ScrollRightAction,
    ScrollUpAction,
    SelectOption,
    TaskComplete,
    Uncheck,
    action_definitions,
)
from .functions import *


def custom_json_schema(action_function: type[BaseModel]) -> dict:
    schema = action_function.model_json_schema()
    return {
        "action_name": action_function.__name__,
        "action_description": schema.get("description", action_function.__name__),
        "action_params": {
            field: {
                "param_description": schema["properties"][field]["description"],
                "param_type": schema["properties"][field]["type"],
            }
            for field in schema["properties"]
        },
    }


def get_action_signature(action_type: ActionTypes) -> dict:
    return custom_json_schema(action_definitions[action_type])


def get_action_object(action_type: ActionTypes) -> BaseModel:
    return action_definitions[action_type]


def apply_action(action: BaseModel, page: playwright.sync_api.Page = None):
    if isinstance(action, ClickAction):
        click(bid=action.bid, page=page)
    elif isinstance(action, InputText):
        fill(bid=action.bid, value=action.value, page=page)
    elif isinstance(action, ScrollUpAction):
        scroll_up(page=page)
    elif isinstance(action, ScrollDownAction):
        scroll_down(page=page)
    elif isinstance(action, ScrollLeftAction):
        scroll_left(page=page)
    elif isinstance(action, ScrollRightAction):
        scroll_right(page=page)
    elif isinstance(action, SelectOption):
        select_option(bid=action.bid, options=action.options, page=page)
    elif isinstance(action, Check):
        check(bid=action.bid, page=page)
    elif isinstance(action, Uncheck):
        uncheck(bid=action.bid, page=page)
    elif isinstance(action, Hover):
        hover(bid=action.bid, page=page)
    elif isinstance(action, Noop):
        noop(wait_ms=action.wait_ms, page=page)
    elif isinstance(action, TaskComplete):
        return True
    return False


def get_action_string(action: BaseModel):
    string = action.model_dump()
    string["action"] = action.__class__.__name__
    string = json.dumps(string, indent=4)
    return string


def parse_action_string(string) -> BaseModel:
    string: dict = json.loads(string)
    action_class = action_definitions.get(string.pop("action"))
    action = action_class.model_validate(string)
    return action
