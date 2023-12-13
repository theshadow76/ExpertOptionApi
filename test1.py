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
        return self.bot.GetSingleCandles()

    def _assetHistoryCandles(self):
        bot = ExpertOptionAPI(token="76782ad35d33d99cb0ed7bc948919dd8", server_region="wss://fr24g1eu.expertoption.com/")
        bot.connect()
        return self.bot.GetCandlesHistory()  # Use self.bot

class Statistics:
    def __init__(self):
        self.period = 14

    def _CalculateRSI(self, data):
        # Check for the necessary keys in the data
        if 'action' in data and 'message' in data and 'candles' in data['message']:
            candles_data = data['message']['candles']
            
            # Initialize an empty list for closing prices
            closes = []

            # Iterate over each candle data
            for candle in candles_data:
                # Check if 'periods' is in candle
                if 'periods' in candle:
                    for period in candle['periods']:
                        # The closing price is the last element of the last inner list in each period
                        # Check if period data is valid
                        if period and len(period) > 1 and len(period[1]) > 0:
                            close_price = period[1][-1][3]  # Access the closing price
                            closes.append(close_price)

            # If we have closing prices, calculate RSI
            if closes:
                return self._CalculateRSIFromCloses(closes)  # Call the method to calculate RSI from closes

        # Return an empty DataFrame if data is invalid
        return pd.DataFrame(columns=["Close", "RSI"])


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
        df['Avg_Gain'] = df['Gain'].rolling(window=window, min_periods=1).mean()  # Adjusted min_periods
        df['Avg_Loss'] = df['Loss'].rolling(window=window, min_periods=1).mean()  # Adjusted min_periods

        # Calculate RS and RSI
        df['RS'] = df['Avg_Gain'] / df['Avg_Loss']
        df['RSI'] = 100 - (100 / (1 + df['RS']))

        # Option to remove NaN values
        # df = df.dropna(subset=['RSI'])

        return df[['Close', 'RSI']]

class ScalpingIndicator:
    def __init__(self, data, threshold=0.02):
        self.data = data
        self.threshold = threshold
        self.candles = self.parse_data(data)

    def parse_data(self, data):
        # Extract candle data
        return [
            (candle['periods'], candle['tf']) 
            for candle in data['message']['candles']
        ]

    def calculate_percentage_change(self, current_price, reference_price):
        # Calculate the percentage change from the reference price
        return ((current_price - reference_price) / reference_price) * 100

    def is_significant_movement(self, price, reference):
        # Check if price movement is significant (up or down)
        percentage_change = self.calculate_percentage_change(price, reference)
        return abs(percentage_change) >= self.threshold

    def detect_scalping_opportunity(self):
        # Detect scalping opportunity
        last_percentage_change = None

        for periods, tf in self.candles:
            for period in periods:
                timestamp, prices = period
                _, high_price, _, close_price = prices[0]
                # Assuming close price of previous candle as reference
                reference_price = close_price
                for price_data in prices[1:]:
                    _, high, _, close = price_data
                    current_percentage_change = self.calculate_percentage_change(high, reference_price)
                    last_percentage_change = current_percentage_change
                    if self.is_significant_movement(high, reference_price):
                        direction = "up" if current_percentage_change > 0 else "down"
                        print(f"Scalping opportunity detected at {timestamp} on TF {tf}, Direction: {direction}, Change: {current_percentage_change:.2f}%")
                        return f"Scalping opportunity detected at {timestamp} on TF {tf}, Direction: {direction}, Change: {current_percentage_change:.2f}%"

        # If no opportunity was detected, print the last calculated change
        if last_percentage_change is not None:
            print(f"No opportunity detected. Last change: {last_percentage_change:.2f}%")
        else:
            print("No opportunity detected.")

        return "No opportunity detected."
    
    def detect_scalping_opportunity_single_price(self):
        # Initialize variables
        last_price = None
        last_percentage_change = None

        # Detect scalping opportunity
        for periods, tf in self.candles:
            for period in periods:
                timestamp, prices = period
                for price_data in prices:
                    current_price = price_data[0]
                    if last_price is not None:
                        current_percentage_change = self.calculate_percentage_change(current_price, last_price)
                        last_percentage_change = current_percentage_change
                        if self.is_significant_movement(current_price, last_price):
                            direction = "up" if current_percentage_change > 0 else "down"
                            print(f"Scalping opportunity detected at {timestamp} on TF {tf}, Direction: {direction}, Change: {current_percentage_change:.2f}%")
                            return f"Scalping opportunity detected at {timestamp} on TF {tf}, Direction: {direction}, Change: {current_percentage_change:.2f}%"
                    last_price = current_price

        # If no opportunity was detected, print the last calculated change
        if last_percentage_change is not None:
            print(f"No opportunity detected. Last change: {last_percentage_change:.2f}%")
        else:
            print("No opportunity detected.")

        return "No opportunity detected."



class AlligatorIndicator:
    def __init__(self, candles):
        print("Raw candle data:", candles)  # Print the raw candle data

        self.prices = self.extract_prices(candles)
        print("Extracted prices:", self.prices)  # Print the extracted prices

        if self.prices:
            print("Type of first element in prices:", type(self.prices[0]))
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

    def evaluate_market(self, bot):
        # Make sure we have enough data points
        if len(self.jaw) < 2 or len(self.teeth) < 2 or len(self.lips) < 2:
            return "Not enough data"

        # Check the ordering of the lines for the last two data points
        last_order = self.jaw[-1] > self.teeth[-1] > self.lips[-1]
        prev_order = self.jaw[-2] > self.teeth[-2] > self.lips[-2]

        # Check for a buy signal (upward trend)
        if not prev_order and last_order:
            # Execute a buy order
            bot.Buy(amount=1, type="call", assetid=240, exptime=60, isdemo=1, strike_time=int(time.time()))
            return "Buy signal executed"

        # Check for a sell signal (downward trend)
        if prev_order and not last_order:
            # Execute a sell order
            bot.Buy(amount=1, type="put", assetid=240, exptime=60, isdemo=1, strike_time=int(time.time()))
            return "Sell signal executed"
        
        return "hold"


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
print(f"The candles data is: {candles}")
threshold = 1.0  # Set your desired threshold here, e.g., 1%
for i in range(30):
    candles2 = rsi._GetCandlesData()
    indicator = ScalpingIndicator(candles2, threshold)
    idata = indicator.detect_scalping_opportunity()
    print(idata)
    idata2 = indicator.detect_scalping_opportunity_single_price()
    print(idata2)
    alligator = AlligatorIndicator(candles2)
    market_status = alligator.evaluate_market(bot)
    print(market_status)
    time.sleep(60)