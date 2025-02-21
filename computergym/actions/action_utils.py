from .action import ActionTypes
from .interaction_actions import ClickAction, InputText, ScrollAction


def get_action_description(action_type: ActionTypes) -> str:
    """
    Get the description of the action.

    Args:
        action_type (ActionTypes): The type of action.

    Returns:
        str: The description of the action.
    """
    if action_type == ActionTypes.click:
        return ClickAction.get_action_description()
    elif action_type == ActionTypes.input_text:
        return InputText.get_action_description()
    elif action_type == ActionTypes.scroll:
        return ScrollAction.get_action_description()
    else:
        raise ValueError(f"Unknown action type: {action_type}")


def get_parameters_description(action_type: ActionTypes) -> str:
    """
    Get the parameters of the action.

    Args:
        action_type (ActionTypes): The type of action.

    Returns:
        str: The parameters of the action.
    """
    if action_type == ActionTypes.click:
        return ClickAction.get_parameters_description()
    elif action_type == ActionTypes.input_text:
        return InputText.get_parameters_description()
    elif action_type == ActionTypes.scroll:
        return ScrollAction.get_parameters_description()
    else:
        raise ValueError(f"Unknown action type: {action_type}")
