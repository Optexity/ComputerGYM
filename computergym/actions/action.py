from enum import Enum, unique
from typing import Union

from pydantic import BaseModel, Field


class ClickAction(BaseModel):
    """
    Click on an element with the given bid.
    """

    bid: str = Field(description="The id of the element to be clicked.")


class InputText(BaseModel):
    """
    Input text(value) into an element with the given bid.
    """

    bid: str = Field(description="The id of the element to be clicked.")
    value: str = Field(description="The text to be input.")


class ScrollUpAction(BaseModel):
    """
    Scroll the page up by half the height of the page.
    """

    pass


class ScrollDownAction(BaseModel):
    """
    Scroll the page down by half the height of the page.
    """

    pass


class ScrollLeftAction(BaseModel):
    """
    Scroll the page left by half the width of the page.
    """

    pass


class ScrollRightAction(BaseModel):
    """
    Scroll the page right by half the width of the page.
    """

    pass


class SelectOption(BaseModel):
    """
    Select one or multiple options in a <select> element. You can specify
    option value or label to select. Multiple options can be selected.
    """

    bid: str = Field(description="The id of the <select> element")
    options: list[str] = Field(
        description="Select single or multiple options. list of strings even for single option."
    )


@unique
class ActionTypes(Enum):
    """
    Adapted from browsergym/core/src/browsergym/core/action/highlevel.py
    """

    # INTERACTION ACTIONS
    click = "click"
    scroll_up = "scroll_up"
    scroll_down = "scroll_down"
    scroll_left = "scroll_left"
    scroll_right = "scroll_right"
    input_text = "input_text"
    hover = "hover"
    select_option = "select_option"

    # TAB ACTIONS
    tab_focus = "tab_focus"
    tab_close = "tab_close"
    new_tab = "new_tab"

    # NAVIGATION ACTIONS
    go_back = "go_back"
    go_forward = "go_forward"
    refresh = "refresh"


action_definitions: dict[ActionTypes, BaseModel] = {
    ActionTypes.click: ClickAction,
    ActionTypes.input_text: InputText,
    ActionTypes.scroll_up: ScrollUpAction,
    ActionTypes.scroll_down: ScrollDownAction,
    ActionTypes.scroll_left: ScrollLeftAction,
    ActionTypes.scroll_right: ScrollRightAction,
    ActionTypes.select_option: SelectOption,
}

action_examples: dict[ActionTypes, BaseModel] = {
    ActionTypes.click: ClickAction(bid="12"),
    ActionTypes.input_text: InputText(bid="12", value="Hello world!"),
    ActionTypes.scroll_up: ScrollUpAction(),
    ActionTypes.scroll_down: ScrollDownAction(),
    ActionTypes.scroll_left: ScrollLeftAction(),
    ActionTypes.scroll_right: ScrollRightAction(),
    ActionTypes.select_option: SelectOption(bid="c48", options=["red", "green"]),
}
