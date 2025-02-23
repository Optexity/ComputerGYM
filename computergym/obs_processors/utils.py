from computergym.obs_processors import (
    ObsProcessorTypes,
    axtree_processor,
    html_processor,
    screenshot_processor,
    som_processor,
)
from computergym.utils import save_screenshot


def format_obs(obs, obs_processors, cache_dir: str, current_step: int):
    temp = {
        "chat_messages": obs["chat_messages"],
        "screenshot": obs["screenshot"],
        "goal_object": obs["goal_object"],
        "last_action": obs["last_action"],
        "last_action_error": obs["last_action_error"],
        "open_pages_urls": obs["open_pages_urls"],
        "open_pages_titles": obs["open_pages_titles"],
        "active_page_index": obs["active_page_index"],
    }

    for processor in obs_processors:
        if processor == ObsProcessorTypes.html:
            temp[processor] = html_processor(obs["dom_object"])
        elif processor == ObsProcessorTypes.axtree:
            temp[processor] = axtree_processor(obs["axtree_object"])
        elif processor == ObsProcessorTypes.screenshot:
            temp[processor] = screenshot_processor(obs["screenshot"])
            save_screenshot(
                temp[processor],
                cache_dir,
                f"screenshot-{current_step}.png",
            )
        elif processor == ObsProcessorTypes.som:
            temp[processor] = som_processor(
                obs["screenshot"], obs["extra_element_properties"]
            )
            save_screenshot(temp[processor], cache_dir, f"som-{current_step}.png")
        else:
            print(f"Warning: ObsProcessor {processor} not implemented. Skipping.")
    return temp
