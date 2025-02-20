from enum import Enum, unique
from typing import Any, Callable

from browsergym.utils.obs import flatten_axtree_to_str, flatten_dom_to_str, prune_html


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

        def func(dom_object):
            return prune_html(flatten_dom_to_str(dom_object))

        return func
    if obs_processor_type == ObsProcessorTypes.axtree:
        return flatten_axtree_to_str
    if obs_processor_type == ObsProcessorTypes.screenshot:
        pass
    if obs_processor_type == ObsProcessorTypes.som:
        pass
    if obs_processor_type == ObsProcessorTypes.omniparser:
        pass
