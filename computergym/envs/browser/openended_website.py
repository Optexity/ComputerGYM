import browsergym.core
import gymnasium as gym
from computergym.actions import ActionTypes
from computergym.obs_processors import ObsProcessorTypes, get_obs_processor_function


class OpenEndedWebsite(gym.Env):
    def __init__(self, url: str, obs_processors: list[ObsProcessorTypes]):
        self.url = url
        self.obs_processors = obs_processors
        self.obs_processors_functions = [
            get_obs_processor_function(x) for x in obs_processors
        ]
        self.history = []
        self.obs = {}
        self.action = None
        self.terminated = False
        self.truncated = False
        self.info = {}

        self.action_space = [ActionTypes.click, ActionTypes.input_text]

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

        for processor, function in zip(
            self.obs_processors, self.obs_processors_functions
        ):
            if processor == ObsProcessorTypes.html:
                temp[processor] = function(obs["dom_object"])
            elif processor == ObsProcessorTypes.axtree:
                temp[processor] = function(obs["axtree_object"])
            else:
                temp[processor] = function(obs[processor])
        return temp

    def reset(self):
        ## TODO: remove self.env when we implement our own environment
        obs, info = self.env.reset()
        self.obs = self.format_obs(obs)
        return self.obs, info

    def step(self, action):
        ## TODO: remove self.env when we implement our own environment
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
