# Bot using the RSI indicator

# imports
from ExpertOptionAPI.expert import EoApi as ExpertOptionAPI
import numpy as np


# module
class RSI:
    def __ini__(self, token: str):
        self.token = token
        self.bot = ExpertOptionAPI(token=token, server_region="wss://fr24g1eu.expertoption.com/")
    def _GetCandlesData(self):
        data = self.bot.GetCandles()
        return data

class Statistics:
    def __init__(self):
        self.period = 14
    def _CalculateRSI(self, closes):
        changes = np.diff(closes)
        gains = np.where(changes > 0, changes, 0)
        losses = np.where(changes < 0, -changes, 0)

        avg_gain = np.mean(gains[:self.period])
        avg_loss = np.mean(losses[:self.period])

        for i in range(self.period, len(gains)):
            avg_gain = (avg_gain * (self.period - 1) + gains[i]) / self.period
            avg_loss = (avg_loss * (self.period - 1) + losses[i]) / self.period

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

# Test usage
rsi = RSI(token="76782ad35d33d99cb0ed7bc948919dd8")
candles = rsi._GetCandlesData()
print(f"The candles data is: {candles}")