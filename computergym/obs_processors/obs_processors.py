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
