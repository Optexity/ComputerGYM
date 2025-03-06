import logging

from computergym.obs_processors import (
    ObsProcessorTypes,
    axtree_processor,
    html_processor,
    screenshot_processor,
    som_processor,
)

logger = logging.getLogger(__name__)


def format_obs(obs, obs_processors):

    temp = {
        "chat_messages": obs["chat_messages"],
        "screenshot": obs["screenshot"],
        ObsProcessorTypes.goal: obs["goal_object"],
        "last_action": obs["last_action"],
        ObsProcessorTypes.last_action_error: obs["last_action_error"],
        "open_pages_urls": obs["open_pages_urls"],
        "open_pages_titles": obs["open_pages_titles"],
        "active_page_index": obs["active_page_index"],
    }

    for processor in obs_processors:
        if processor == ObsProcessorTypes.html:
            temp[processor] = html_processor(obs["dom_object"])
        elif processor == ObsProcessorTypes.axtree:
            temp[processor] = axtree_processor(
                obs["axtree_object"], obs["extra_element_properties"]
            )
        elif processor == ObsProcessorTypes.screenshot:
            temp[processor] = screenshot_processor(obs["screenshot"])
        elif processor == ObsProcessorTypes.som:
            temp[processor] = som_processor(
                obs["screenshot"], obs["extra_element_properties"]
            )
        else:
            logger.warning(f"ObsProcessor {processor} not implemented. Skipping.")
    return temp
