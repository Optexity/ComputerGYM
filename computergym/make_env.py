from typing import Any

import gymnasium as gym
from computergym.envs.browser.openended_website import OpenEndedWebsite

from .envs import EnvTypes
from .obs_processors import ObsProcessorTypes


def make_env(
    env_name: str, url: str, env_type: EnvTypes, obs_processors: list[ObsProcessorTypes]
) -> Any[gym.Env, OpenEndedWebsite]:

    if env_type == EnvTypes.browser:
        return OpenEndedWebsite(url, obs_processors)
    if env_type == EnvTypes.computer:
        pass

    return None
