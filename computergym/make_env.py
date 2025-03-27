import os

import gymnasium as gym

import playwright.sync_api

from .envs import BrowserEnvTypes, EnvTypes, OpenEndedWebsite


def workarena_preprocess(page: playwright.sync_api.Page):
    page.fill("#user_name", os.environ["SNOW_INSTANCE_UNAME"])
    page.fill("#user_password", os.environ["SNOW_INSTANCE_PWD"])
    page.click("#sysverb_login")


def make_env(
    url: str,
    env_type: EnvTypes,
    browser_env_type: BrowserEnvTypes,
    cache_dir: str = None,
    goal_message: str = None,
    headless: bool = False,
    proxy: str = None,
    storage_state: str = None,
) -> gym.Env | OpenEndedWebsite:

    if env_type == EnvTypes.browser:
        preprocess_func = None
        if browser_env_type == BrowserEnvTypes.workarena:
            preprocess_func = workarena_preprocess
        return OpenEndedWebsite(
            url,
            goal_message,
            cache_dir=cache_dir,
            preprocess_func=preprocess_func,
            headless=headless,
            proxy=proxy,
            storage_state=storage_state,
        )
    if env_type == EnvTypes.computer:
        pass

    return None
