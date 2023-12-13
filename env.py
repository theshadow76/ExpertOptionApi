import gym
from gym import spaces
import numpy as np
from gym.envs.registration import register

from expert import EoApi


class ExpertOptionTradingEnv(gym.Env):

    def __init__(self, render_mode=None, size=500):
        """Add here the code to init everythibng"""
        self.num_steps = size
        self.current_setps = 0

        # Conseguir data basico como balance y el precio del asset y el historical data

    def _get_obs(self):
        """Consigue el data"""

    def reset(self, seed=None, options=None):
        """reiniciar"""

    def step(self, action):
        """Actinoes"""

class _Utils:
    def __init__(self):
        self.token = "76782ad35d33d99cb0ed7bc948919dd8"
        self.server_region = "wss://fr24g1eu.expertoption.com/"
        self.ExpertAPI = EoApi(token=self.token, server_region=self.token)

        self.ExpertAPI.connect()
    def Getbalance(self):
        profile = self.ExpertAPI.Profile()
        print(f"The data for profile is: {profile}") 

util = _Utils()
util.Getbalance()