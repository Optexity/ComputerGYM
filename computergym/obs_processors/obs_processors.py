from enum import Enum, unique


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
