import gym
from gym import spaces
import numpy as np
from gym.envs.registration import register
import random
import yfinance as yf


class ExpertOptionTradingEnv(gym.Env):
    def __init__(self, render_mode=None, size=500):
        super().__init__()
        self.num_steps = size
        self.current_steps = 0
        self.utils = _Utils()

        observation_length = 10

        # Observation space: current price, price history, and account balance
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf,
                                            shape=(observation_length,), dtype=np.float32)


        # Action space: 0 - Do nothing, 1 - Buy, 2 - Sell
        self.action_space = spaces.Discrete(3)

        # Initialize Alligator Indicator
        self.alligator_indicator = None

    def _get_obs(self):
        # Ensure that current_step doesn't exceed the length of historical data
        if self.current_step >= len(self.utils.hist):
            self.current_step = 0  # Reset to start for continuous training

        # Fetch historical price data up to the current step
        historical_prices = self.utils.GetCandlesData()[:self.current_step + 1]
        current_price = historical_prices[-1]
        balance = self.utils.Getbalance()

        # Ensure historical_prices has the correct length
        historical_prices = historical_prices[-self.num_steps:]

        # Initialize Alligator Indicator with historical prices
        self.alligator_indicator = _AlligatorIndicator(historical_prices)


        return {
            "current_price": np.array([current_price], dtype=np.float32),
            "price_history": np.array(historical_prices, dtype=np.float32),
            "account_balance": np.array([balance], dtype=np.float32),
        }
    def reset(self, seed=None, options=None):
        # Start from a random point in the historical data
        max_start_index = len(self.utils.hist) - self.num_steps
        self.current_steps = random.randint(0, max_start_index) if max_start_index > 0 else 0
        return self._get_obs()

    def step(self, action):
        # Retrieve the market signal from the Alligator Indicator
        market_signal = self.alligator_indicator.evaluate_market()

        # Initialize reward, done flag, and info dictionary
        reward = 0
        done = False
        info = {}

        # Get current and next price for comparison
        current_price = self.utils.GetCandlesData()[self.current_steps]
        next_price = self.utils.GetCandlesData()[min(self.current_steps + 1, len(self.utils.GetCandlesData()) - 1)]

        # Determine if the price went up or down
        price_went_up = next_price > current_price

        # Logic based on the action taken by the agent
        if action == 0:  # Do nothing
            if market_signal != "hold":
                reward -= 5
        elif action == 1:  # Buy
            if price_went_up:
                reward += 10  # Reward if price went up after buying
            else:
                reward -= 10  # Penalize if price went down after buying
        elif action == 2:  # Sell
            if not price_went_up:
                reward += 10  # Reward if price went down after selling
            else:
                reward -= 10  # Penalize if price went up after selling

        # Update the current step and check if the episode is done
        self.current_steps += 1
        if self.current_steps >= self.num_steps:
            done = True

        # Update the state (observation)
        new_observation = self._get_obs()

        # Optionally adjust the reward based on the market signal
        if market_signal == "buy" and action == 1 or market_signal == "sell" and action == 2:
            reward += 3
        elif market_signal == "buy" and action == 2 or market_signal == "sell" and action == 1:
            reward -= 3

        # Return the new observation, reward, whether the episode is done, and additional info
        return new_observation, reward, done, info


class _Utils:
    def __init__(self, ticker="MSFT", start='2018-01-01', end='2023-01-01'):
        self.msft = yf.Ticker(ticker)
        self.hist = self.msft.history(period="1d", start=start, end=end)

    def GetLatestPrice(self):
        # Return the latest available closing price
        return self.hist['Close'].iloc[-1]

    def GetCandlesData(self):
        # Return the closing prices
        return self.hist['Close'].tolist()

    def Getbalance(self):
        # Mock balance for the demonstration
        return 10000  # Example balance

class _AlligatorIndicator:
    def __init__(self, prices):
        self.prices = prices
        if self.prices:
            self.jaw = self.smoothed_moving_average(13, 8)
            self.teeth = self.smoothed_moving_average(8, 5)
            self.lips = self.smoothed_moving_average(5, 3)
        else:
            print("Prices is empty")

    def extract_prices(self, candles):
        # Extract the closing price from each candle
        prices = []
        for candle in candles['message']['candles']:
            for period in candle['periods']:
                timestamp, price_data = period
                for data in price_data:
                    closing_price = data[3]  # Assuming the closing price is the fourth element
                    prices.append(closing_price)
        return prices

    def smoothed_moving_average(self, period, shift):
        # Simple Moving Average calculation
        sma = np.convolve(self.prices, np.ones(period), 'valid') / period
        # Return shifted SMA
        return np.concatenate((np.full(shift, np.nan), sma))

    def evaluate_market(self):
        # Make sure we have enough data points
        if len(self.jaw) < 2 or len(self.teeth) < 2 or len(self.lips) < 2:
            return "Not enough data"

        # Check the ordering of the lines for the last two data points
        last_order = self.jaw[-1] > self.teeth[-1] > self.lips[-1]
        prev_order = self.jaw[-2] > self.teeth[-2] > self.lips[-2]

        # Check for a buy signal (upward trend)
        if not prev_order and last_order:
            return "buy"

        # Check for a sell signal (downward trend)
        if prev_order and not last_order:
            return "sell"
        
        return "hold"

register(
    id='ExpertOptionTrading-v0',
    entry_point='expert_option_trading:ExpertOptionTradingEnv',
)