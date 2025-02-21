import browsergym.core
import gymnasium as gym
import numpy as np
from computergym.actions import ActionTypes
from computergym.obs_processors import (
    ObsProcessorTypes,
    axtree_processor,
    html_processor,
    screenshot_processor,
    som_processor,
)
from PIL import Image


# Convert numpy array to PIL Image and save
def save_screenshot(screenshot_array, filename="screenshot.png"):
    if isinstance(screenshot_array, np.ndarray):
        img = Image.fromarray(screenshot_array)
        img.save(filename)


class OpenEndedWebsite(gym.Env):
    def __init__(self, url: str, obs_processors: list[ObsProcessorTypes]):
        self.url = url
        self.obs_processors = obs_processors
        self.history = []
        self.obs = {}
        self.action = None
        self.terminated = False
        self.truncated = False
        self.info = {}

        self.action_space = [
            ActionTypes.click,
            ActionTypes.input_text,
            ActionTypes.scroll,
        ]

        ## TODO: remove this when we implement our own environment
        self.env = gym.make(
            "browsergym/openended",
            task_kwargs={"start_url": url},  # starting URL
            wait_for_user_message=True,  # wait for a user message after each agent message sent to the chat
            headless=False,  # run the browser in headless mode
        )

    def format_obs(self, obs):
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

        for processor in self.obs_processors:
            if processor == ObsProcessorTypes.html:
                temp[processor] = html_processor(obs["dom_object"])
            elif processor == ObsProcessorTypes.axtree:
                temp[processor] = axtree_processor(obs["axtree_object"])
            elif processor == ObsProcessorTypes.screenshot:
                temp[processor] = screenshot_processor(obs["screenshot"])
                save_screenshot(temp[processor], "screenshot.png")
            elif processor == ObsProcessorTypes.som:
                temp[processor] = som_processor(
                    obs["screenshot"], obs["extra_element_properties"]
                )
                save_screenshot(temp[processor], "som.png")
            else:
                print(f"Warning: ObsProcessor {processor} not implemented. Skipping.")
        return temp

    def reset(self):
        ## TODO: remove self.env when we implement our own environment
        obs, info = self.env.reset()
        self.obs = self.format_obs(obs)
        return self.obs, info

    def get_browser_gym_action(
        self, action_type: ActionTypes, action_params: list[str | int]
    ):
        ## TODO: this currently is to handle browsergym actions
        if action_type == ActionTypes.click:
            new_params = [f'"{param}"' for param in action_params]
            return f"""```{action_type.value}({','.join(new_params)})```"""
        elif action_type == ActionTypes.input_text:
            new_params = [f'"{param}"' for param in action_params]
            return f"""```fill({','.join(new_params)})```"""
        elif action_type == ActionTypes.scroll:
            # For scroll, convert params to int and don't add quotes
            new_params = [str(int(param)) for param in action_params]
            return f"""```scroll({','.join(new_params)})```"""

        raise ValueError(
            f"Invalid action type: {action_type}. Supported types are: {self.action_space}"
        )

    def step(self, action_type: ActionTypes, action_params: list[str]):
        ## TODO: remove self.env when we implement our own environment
        action = self.get_browser_gym_action(action_type, action_params)
        obs, reward, terminated, truncated, info = self.env.step(action)
        self.obs = self.format_obs(obs)
        return self.obs, reward, terminated, truncated, info
        self.obs = {}
        self.main_observation = {}
        for processor in self.obs_processors:
            self.obs[processor] = self.obs_processors[processor](self.main_observation)
        return self.obs

    def render(self):
        pass

    def close(self):
        ## TODO: remove this when we implement our own environment
        self.env.close()

    def seed(self, seed=None):
        pass

    def get_action_space(self) -> list[ActionTypes]:
        return self.action_space

    def get_observation_space(self) -> list[ObsProcessorTypes]:
        pass
