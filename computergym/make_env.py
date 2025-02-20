from enum import Enum

from computergym.envs.browser.openended_website import OpenEndedWebsite

from .obs_processors import ObsProcessorTypes


class EnvTypes(Enum):
    browser = "browser"
    computer = "computer"


def make_env(env_name: str, env_type: str, obs_processors: list[str]):
    env_type = EnvTypes[env_type]
    obs_processors = [
        ObsProcessorTypes[obs_processor] for obs_processor in obs_processors
    ]
    if env_type == EnvTypes.browser:
        return OpenEndedWebsite(obs_processors)
    if env_type == EnvTypes.computer:
        pass

    return None
