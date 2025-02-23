from enum import Enum, unique

from pydantic import BaseModel, Field


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


class ClickAction(BaseModel):
    element_id: str = Field(description="The id of the element to be clicked.")


class InputText(BaseModel):
    element_id: str = Field(description="The id of the element to be clicked.")
    value: str = Field(description="The text to be input.")


class ScrollAction(BaseModel):
    pass
