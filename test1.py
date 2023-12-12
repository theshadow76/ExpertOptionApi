# Bot using the RSI indicator

# imports
from expert import EoApi as ExpertOptionAPI
import numpy as np
import time
import pandas as pd

# module
class RSI:
    def __init__(self):  # Correct the __init__ method
        self.token = "76782ad35d33d99cb0ed7bc948919dd8"
        self.bot = ExpertOptionAPI(token=self.token, server_region="wss://fr24g1eu.expertoption.com/")
    
    def _GetCandlesData(self):
        bot = ExpertOptionAPI(token="76782ad35d33d99cb0ed7bc948919dd8", server_region="wss://fr24g1eu.expertoption.com/")
        bot.connect()
        return self.bot.GetCandles()  # Use self.bot

    def _assetHistoryCandles(self):
        bot = ExpertOptionAPI(token="76782ad35d33d99cb0ed7bc948919dd8", server_region="wss://fr24g1eu.expertoption.com/")
        bot.connect()
        return self.bot.GetCandlesHistory()  # Use self.bot

class Statistics:
    def __init__(self):
        self.period = 14

    def _CalculateRSI(self, data):
        # Extract closing prices from the data
        if 'action' in data and 'message' in data and 'candles' in data['message']:
            candles_data = data['message']['candles']
            if candles_data and 'periods' in candles_data[0]:
                periods = candles_data[0]['periods']
                closes = [period[1][-1][0] for period in periods if period[1]]
                return self._CalculateRSIFromCloses(closes)  # Call the method to calculate RSI from closes
            
        return pd.DataFrame(columns=["Close", "RSI"])  # Return an empty DataFrame if data is invalid

    def _CalculateRSIFromCloses(self, closes):
        # Converting to a DataFrame
        df = pd.DataFrame(closes, columns=["Close"])

        # Calculate the difference in price
        df['Delta'] = df['Close'].diff()

        # Calculate gains and losses
        df['Gain'] = df['Delta'].apply(lambda x: x if x > 0 else 0)
        df['Loss'] = df['Delta'].apply(lambda x: -x if x < 0 else 0)

        # Calculate the average gain and loss
        window = 14  # Or use self.period if you want to use the period defined in __init__
        df['Avg_Gain'] = df['Gain'].rolling(window=window).mean()
        df['Avg_Loss'] = df['Loss'].rolling(window=window).mean()

        # Calculate RS and RSI
        df['RS'] = df['Avg_Gain'] / df['Avg_Loss']
        df['RSI'] = 100 - (100 / (1 + df['RS']))

        return df[['Close', 'RSI']]

# Your bot initialization and usage code
# [Rest of your bot code]


bot = ExpertOptionAPI(token="76782ad35d33d99cb0ed7bc948919dd8", server_region="wss://fr24g1eu.expertoption.com/")
bot.connect()

data1 = int(time.time()) - 60000
data2 = int(time.time()) - 10000

print(f"The data 1 is: {data1} and the 2 is: {data2}")

periods = [data1, data2]

# Test usage
# Initialize RSI class and connect to the API
rsi = RSI()
# Assuming that the RSI class connects to the API in its __init__ method
# Otherwise, you might need to call a connect method here

# Retrieve candle data
assetHistoryCandles = rsi._assetHistoryCandles()
candles = rsi._GetCandlesData()

# Check the output of assetHistoryCandles
print("Asset History Candles:", candles)

# Initialize Statistics class
rsiStats = Statistics()

# Calculate RSI using the retrieved data
data = rsiStats._CalculateRSI(data=candles)

# Print the RSI data
print(data)
