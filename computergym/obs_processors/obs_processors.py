from enum import Enum


class ObsProcessorTypes(Enum):
    html = "html"
    axtree = "axtree"
    screenshot = "screenshot"
    som = "som"
    omniparser = "omniparser"


def get_obs_processor_function(obs_processor_type: ObsProcessorTypes) -> function:
    if obs_processor_type == ObsProcessorTypes.html:
        pass
    if obs_processor_type == ObsProcessorTypes.axtree:
        pass
    if obs_processor_type == ObsProcessorTypes.screenshot:
        pass
    if obs_processor_type == ObsProcessorTypes.som:
        pass
    if obs_processor_type == ObsProcessorTypes.omniparser:
        pass
