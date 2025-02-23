from pydantic import BaseModel

from .action import (
    ActionTypes,
    ClickAction,
    InputText,
    ScrollAction,
    action_definitions,
)
from .functions import click, fill, scroll


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


def apply_action(action: BaseModel, page=None) -> BaseModel:
    if isinstance(action, ClickAction):
        click(bid=action.element_id, page=page)
    elif isinstance(action, InputText):
        fill(bid=action.element_id, value=action.value)
    elif isinstance(action, ScrollAction):
        scroll(0, 200)
