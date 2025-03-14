import gymnasium as gym
import playwright.sync_api
from computergym.envs.browser.openended_website import OpenEndedWebsite

from .envs import BrowserEnvTypes, EnvTypes
from .obs_processors import ObsProcessorTypes


def make_env(
    url: str,
    env_type: EnvTypes,
    browser_env_type: BrowserEnvTypes,
    obs_processors: list[ObsProcessorTypes],
    cache_dir: str = None,
    goal_message: str = None,
    headless: bool = False,
    proxy: str = None,
) -> gym.Env | OpenEndedWebsite:

    def workarena_preprocess(page: playwright.sync_api.Page):
        page.fill("#user_name", "admin")
        page.fill("#user_password", "wx%h/z5WWW0J")
        page.click("#sysverb_login")

    if env_type == EnvTypes.browser:
        preprocess_func = None
        if browser_env_type == BrowserEnvTypes.workarena:
            preprocess_func = workarena_preprocess
        return OpenEndedWebsite(
            url,
            obs_processors,
            goal_message,
            cache_dir=cache_dir,
            preprocess_func=preprocess_func,
            headless=headless,
            proxy=proxy,
        )
    if env_type == EnvTypes.computer:
        pass

    return None
