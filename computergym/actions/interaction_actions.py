from .action import Action, ActionTypes
from .functions import *


class ClickAction(Action):
    """
    Represents a click action in the ComputerGYM environment.
    """

    def __init__(self):
        """
        Initialize the ClickAction class.
        """
        super().__init__(ActionTypes.click)

    @staticmethod
    def get_action_description():
        description = f"""Click on element with ID."""
        return description

    @staticmethod
    def get_parameters_description():
        description = f"""This takes single args -> ID of the element to be clicked. ID must be an integer."""
        return description


class InputText(Action):
    """
    Represents an input text action in the ComputerGYM environment.
    """

    def __init__(self):
        """
        Initialize the InputText class.
        """
        super().__init__(ActionTypes.input_text)

    @staticmethod
    def get_action_description():
        description = f"""Input text into element with ID."""
        return description

    @staticmethod
    def get_parameters_description():
        description = f"""This takes two args -> ID of the element to input text. ID must be a integer. Text to be input. Text must be a string.
        Example: {ActionTypes.input_text.value}(int_input_id, "Hello World!")"""
        return description


class ScrollAction(Action):
    """
    Represents a scroll action in the ComputerGYM environment.
    """

    def __init__(self):
        """
        Initialize the ScrollAction class.
        """
        super().__init__(ActionTypes.scroll)

    @staticmethod
    def get_action_description():
        description = f"""Scroll the page with a given amount of pixels horizontally and vertically. Dispatches a wheel event."""
        return description

    @staticmethod
    def get_parameters_description():
        description = f"""Amounts in pixels as integers, positive for right or down scrolling, negative for left or up scrolling.
        Examples: {ActionTypes.scroll.value}(0, 200), {ActionTypes.scroll.value}(-50, -100)"""
        return description
