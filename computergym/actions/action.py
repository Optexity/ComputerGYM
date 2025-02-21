from enum import Enum, unique


@unique
class ActionTypes(Enum):
    """
    Adapted from browsergym/core/src/browsergym/core/action/highlevel.py
    """

    # INTERACTION ACTIONS
    click = "click"
    scroll = "scroll"
    input_text = "input_text"
    hover = "hover"

    # TAB ACTIONS
    tab_focus = "tab_focus"
    tab_close = "tab_close"
    new_tab = "new_tab"

    # NAVIGATION ACTIONS
    go_back = "go_back"
    go_forward = "go_forward"
    refresh = "refresh"


class Action:
    """
    Base class for all actions in the ComputerGYM environment.
    """

    def __init__(self, action_type: ActionTypes):
        """
        Initialize the Action class.

        Args:
            action_type (str): The type of action.
        """
        self.action_type = action_type
        self.action_name = action_type.value
        self.action_params = {}

    @staticmethod
    def get_action_description():
        """
        Get the description of the action.

        Returns:
            str: The description of the action.
        """
        raise NotImplementedError(
            "This method should be overridden by subclasses to provide action descriptions."
        )

    @staticmethod
    def get_parameters_description():
        """
        Get the parameters of the action.

        Returns:
            dict: The parameters of the action.
        """
        raise NotImplementedError(
            "This method should be overridden by subclasses to provide action parameters."
        )

    def do_action(self, *args, **kwargs):
        """
        Execute the action.

        Returns:
            bool: True if the action was successful, False otherwise.
        """
        raise NotImplementedError(
            "This method should be overridden by subclasses to provide action execution"
        )
