from pydantic import BaseModel, Field

from .functions import *


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


class Check(BaseModel):
    """
    Check a checkbox or radio element with the given bid.
    """

    bid: str = Field(description="The id of the element to be checked.")


class Uncheck(BaseModel):
    """
    Uncheck a checkbox or radio element with the given bid.
    """

    bid: str = Field(description="The id of the element to be unchecked.")


class Hover(BaseModel):
    """
    Hover over an element with the given bid.
    """

    bid: str = Field(description="The id of the element to be hovered over.")


class Noop(BaseModel):
    """
    No operation, wait for a given number of milliseconds before the next action.
    """

    wait_ms: int = Field(
        description="The number of milliseconds to wait before the next action."
    )


class TaskComplete(BaseModel):
    """
    This action is used to indicate that the task is complete.
    """

    msg: str = Field(
        description="The message to be displayed when the task is complete."
    )


all_action_types = [
    ClickAction,
    InputText,
    ScrollUpAction,
    ScrollDownAction,
    ScrollLeftAction,
    ScrollRightAction,
    SelectOption,
    Check,
    Uncheck,
    Hover,
    Noop,
    TaskComplete,
]

string_to_action_type: dict[str, type[BaseModel]] = {
    action_type.__name__: action_type for action_type in all_action_types
}

action_examples: dict[str, BaseModel] = {
    ClickAction.__name__: ClickAction(bid="12"),
    InputText.__name__: InputText(bid="12", value="Hello world!"),
    ScrollUpAction.__name__: ScrollUpAction(),
    ScrollDownAction.__name__: ScrollDownAction(),
    ScrollLeftAction.__name__: ScrollLeftAction(),
    ScrollRightAction.__name__: ScrollRightAction(),
    SelectOption.__name__: SelectOption(bid="c48", options=["red", "green"]),
    Check.__name__: Check(bid="12"),
    Uncheck.__name__: Uncheck(bid="12"),
    Hover.__name__: Hover(bid="12"),
    Noop.__name__: Noop(wait_ms=1000),
    TaskComplete.__name__: TaskComplete(msg="Task completed successfully!"),
}


assert len(all_action_types) == len(
    set([action_type.__name__ for action_type in all_action_types])
), "Action types must have unique names"


assert len(action_examples) == len(
    all_action_types
), "All action types must have examples"


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
