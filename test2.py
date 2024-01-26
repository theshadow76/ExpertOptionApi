import numpy as np
import datetime
import pandas as pd
import json
from ExpertOptionAPI.expert import EoApi as ExpertAPI

class Stock:

    ticker = None
    dates = None
    closes = None
    highs = None
    lows = None
    opens = None
    volumes = None
    rsi = None

    def __init__(self):
        pass
    def load_data_from_json(self, json_data):
        """
        Parse the provided JSON data and populate the class attributes.
        """
        data = json.loads(json_data)
        candles = data["message"]["candles"][0]["periods"]

        # Assuming each sublist in periods contains [timestamp, [open, high, low, close, volume]]
        self.opens = np.array([item[1][0][0] for item in candles])
        self.highs = np.array([item[1][0][1] for item in candles])
        self.lows = np.array([item[1][0][2] for item in candles])
        self.closes = np.array([item[1][0][3] for item in candles])
        self.volumes = np.array([item[1][0][4] if len(item[1][0]) > 4 else np.nan for item in candles])
        self.dates = np.array([item[0] for item in candles])

        # Calculate RSI for the new data
        self.rsi = self.RSI(self.closes)

    def RSI(self, prices, n=14):
        deltas = np.diff(prices)
        seed = deltas[:n+1]
        up = seed[seed >= 0].sum()/n
        down = -seed[seed < 0].sum()/n
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:n] = 100. - 100./(1.+rs)

        for i in range(n, len(prices)):
            delta = deltas[i-1]  # The diff is 1 shorter

            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(n-1) + upval)/n
            down = (down*(n-1) + downval)/n

            rs = up/down
            rsi[i] = 100. - 100./(1.+rs)

        return rsi

    def SMA(self, period, values=None):

        values = self.closes if values is None else values

        """
        Simple Moving Average. Periods are the time frame. For example, a period of 50 would be a 50 day
        moving average. Values are usually the stock closes but can be passed any values
        """

        weigths = np.repeat(1.0, period)/period
        smas = np.convolve(values, weigths, 'valid')
        return smas  # as a numpy array

    def EMA(self, period, values=None):

        values = self.closes if values is None else values

        """
        Exponential Moving Average. Periods are the time frame. For example, a period of 50 would be a 50 day
        moving average. Values are usually the stock closes but can be passed any values
        """

        weights = np.exp(np.linspace(-1., 0., period))
        weights /= weights.sum()
        a = np.convolve(values, weights, mode='full')[:len(values)]
        a[:period] = a[period]
        return a

    def MACD(self, x, slow=26, fast=12):
        """
        Compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
        return value is emaslow, emafast, macd which are len(x) arrays
        """

        emaslow = self.EMA(slow, x)
        emafast = self.EMA(fast, x)
        return emaslow, emafast, emafast - emaslow
    def decide_action(self):
        # Get the latest data
        current_price = self.closes.iloc[-1]
        current_rsi = self.rsi[-1]
        current_sma = self.SMA(50)[-1]
        current_ema = self.EMA(50)[-1]
        macd_slow, macd_fast, macd = self.MACD(self.closes)

        # Decision based on RSI
        if current_rsi < 30:
            return "Buy"
        elif current_rsi > 70:
            return "Sell"

        # Decision based on SMA and EMA
        if current_price > current_sma and current_price > current_ema:
            return "Buy"
        elif current_price < current_sma and current_price < current_ema:
            return "Sell"

        # Decision based on MACD
        if macd[-1] > 0 and macd[-2] < 0:
            return "Buy"
        elif macd[-1] < 0 and macd[-2] > 0:
            return "Sell"

        return "Hold"

# Create an instance of the Stock class
stock = Stock()

# Initialize the expert object with the logger
expert = ExpertAPI(token="aef81ccbb083cde408c3f3510af632bb", server_region="wss://fr24g1eu.expertoption.com/")

expert.connect()

expert.SetDemo()

candles = expert.GetCandles()
print(f"The candles are: {candles}")

# Load the data from JSON
stock.load_data_from_json(json_data=candles)

# Now you can use the methods of the class
# For example, to calculate the RSI
rsi_values = stock.RSI(stock.closes)

# To get a decision based on the loaded data
decision = stock.decide_action()

# Print the decision
print("Decision:", decision)