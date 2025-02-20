from computergym.obs_processors import ObsProcessorTypes, get_obs_processor_function


class OpenEndedWebsite:
    def __init__(self, obs_processors: dict[ObsProcessorTypes, function]):
        self.obs_processors = obs_processors
        self.history = []
        self.main_observation = {}
        self.obs = {}
        self.action = None
        self.terminated = False
        self.truncated = False
        self.info = {}

    def reset(self):
        pass

    def step(self, action):
        self.obs = {}
        self.main_observation = {}
        for processor in self.obs_processors:
            self.obs[processor] = self.obs_processors[processor](self.main_observation)
        return self.obs

    def render(self):
        pass

    def close(self):
        pass

    def seed(self, seed=None):
        pass

    def get_action_space(self):
        pass

    def get_observation_space(self):
        pass
