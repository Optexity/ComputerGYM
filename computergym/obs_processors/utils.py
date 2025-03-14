import logging
import time

import playwright.sync_api
from computergym.obs_processors import (
    ObsProcessorTypes,
    axtree_processor,
    html_processor,
    som_processor,
)
from computergym.obs_processors.observations import (
    MarkingError,
    _post_extract,
    _pre_extract,
    extract_dom_extra_properties,
    extract_dom_snapshot,
    extract_merged_axtree,
    extract_screenshot,
)

logger = logging.getLogger(__name__)
EXTRACT_OBS_MAX_TRIES = 5


def get_observation_from_page(page: playwright.sync_api.Page):
    for retries_left in reversed(range(EXTRACT_OBS_MAX_TRIES)):
        try:
            # pre-extraction, mark dom elements (set bid, set dynamic attributes like value and checked)
            _pre_extract(page)
            dom = extract_dom_snapshot(page)
            axtree = extract_merged_axtree(page)
            extra_properties = extract_dom_extra_properties(dom)
        except (playwright.sync_api.Error, MarkingError) as e:
            err_msg = str(e)
            # try to add robustness to async events (detached / deleted frames)
            if retries_left > 0 and (
                "Frame was detached" in err_msg
                or "Frame with the given frameId is not found" in err_msg
                or "Execution context was destroyed" in err_msg
                or "Frame has been detached" in err_msg
                or "Cannot mark a child frame without a bid" in err_msg
                or "Cannot read properties of undefined" in err_msg
            ):
                logger.warning(
                    f"An error occurred while extracting the dom and axtree. Retrying ({retries_left}/{EXTRACT_OBS_MAX_TRIES} tries left).\n{repr(e)}"
                )
                # post-extract cleanup (ARIA attributes)
                _post_extract(page)
                time.sleep(0.5)
                continue
            else:
                raise e
        break

    # post-extraction cleanup of temporary info in dom
    _post_extract(page)

    # obs is generic to all tasks
    screenshot = extract_screenshot(page)
    obs = {
        ObsProcessorTypes.screenshot: screenshot,
        ObsProcessorTypes.som: som_processor(screenshot, extra_properties),
        ObsProcessorTypes.axtree: axtree_processor(axtree, extra_properties),
        ObsProcessorTypes.html: html_processor(dom),
    }
    return obs
