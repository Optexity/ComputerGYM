from enum import Enum, unique

import numpy as np
from pydantic import BaseModel


@unique
class ObsProcessorTypes(Enum):
    html = "html"
    axtree = "axtree"
    screenshot = "screenshot"
    som = "som"
    omniparser = "omniparser"
    last_action_error = "last_action_error"
    goal = "goal"
    last_action = "last_action"
    open_pages_urls = "open_pages_urls"
    open_pages_titles = "open_pages_titles"
    active_page_index = "active_page_index"
    url = "url"


class Observation:
    def __init__(
        self,
        goal: str,
        open_pages_urls: list[str],
        open_pages_titles: list[str],
        active_page_index: int,
        url: str,
        last_action: BaseModel,
        last_action_error: str,
        html: str,
        axtree: str,
        som: np.array = None,
        screenshot: np.array = None,
    ):
        self.goal = goal
        self.open_pages_urls = open_pages_urls
        self.open_pages_titles = open_pages_titles
        self.active_page_index = active_page_index
        self.url = url
        self.last_action = last_action
        self.last_action_error = last_action_error
        self.html = html
        self.axtree = axtree
        self.som = som
        self.screenshot = screenshot
