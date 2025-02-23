from pydantic import BaseModel

from .action import ActionTypes, ClickAction, InputText, ScrollAction


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
    if action_type == ActionTypes.click:
        return custom_json_schema(ClickAction)
    elif action_type == ActionTypes.input_text:
        return custom_json_schema(InputText)
    elif action_type == ActionTypes.scroll:
        return custom_json_schema(ScrollAction)
    else:
        raise ValueError(f"Unknown action type: {action_type}")


def get_action_object(action_type: ActionTypes) -> BaseModel:
    if action_type == ActionTypes.click:
        return ClickAction
    elif action_type == ActionTypes.input_text:
        return InputText
    elif action_type == ActionTypes.scroll:
        return ScrollAction
    else:
        raise ValueError(f"Unknown action type: {action_type}")
