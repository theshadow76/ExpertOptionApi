# Bot using the RSI indicator

# imports
from expert import EoApi as ExpertOptionAPI
import numpy as np
import time

# module
class RSI:
    def __ini__(self):
        self.token = "76782ad35d33d99cb0ed7bc948919dd8"
        self.bot = ExpertOptionAPI(token="76782ad35d33d99cb0ed7bc948919dd8", server_region="wss://fr24g1eu.expertoption.com/")
    def _GetCandlesData(self):
        data = bot.GetCandles()
        return data
    def _assetHistoryCandles(self):
        data = bot.GetCandlesHistory()
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

bot = ExpertOptionAPI(token="76782ad35d33d99cb0ed7bc948919dd8", server_region="wss://fr24g1eu.expertoption.com/")
bot.connect()

data1 = int(time.time()) - 60000
data2 = int(time.time()) - 10000

print(f"The data 1 is: {data1} and the 2 is: {data2}")

periods = [data1, data2]

# Test usage
rsi = RSI()
candles = rsi._GetCandlesData()
assetHistoryCandles = rsi._assetHistoryCandles()
print(f"The candles data is: {candles}")
print(f"The Historical candles data is: {assetHistoryCandles}")