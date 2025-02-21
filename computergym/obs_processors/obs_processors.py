from enum import Enum, unique
from typing import Any, Callable

from .axtree_processor import axtree_processor
from .html_processor import html_processor


@unique
class ObsProcessorTypes(Enum):
    html = "html"
    axtree = "axtree"
    screenshot = "screenshot"
    som = "som"
    omniparser = "omniparser"


def get_obs_processor_function(
    obs_processor_type: ObsProcessorTypes,
) -> Callable[[Any], str]:
    if obs_processor_type == ObsProcessorTypes.html:
        return html_processor
    if obs_processor_type == ObsProcessorTypes.axtree:
        return axtree_processor
    if obs_processor_type == ObsProcessorTypes.screenshot:
        pass
    if obs_processor_type == ObsProcessorTypes.som:
        pass
    if obs_processor_type == ObsProcessorTypes.omniparser:
        pass
