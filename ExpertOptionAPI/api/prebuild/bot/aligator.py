import numpy as np
from ExpertOptionAPI.expert import EoApi as ExpertAPI
import time

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

# << INIT ExpertAPI >>
expert = ExpertAPI(token="76782ad35d33d99cb0ed7bc948919dd8", server_region="wss://fr24g1eu.expertoption.com/")
expert.connect()

# << LOOP >>
for i in range(50):
    # << GET DATA >>
    candles = expert.GetSingleCandles()

    # << Sample Usage >>
    alligator = AlligatorIndicator(candles)
    market_status = alligator.evaluate_market(expert)
    print(market_status)
    time.sleep(5)