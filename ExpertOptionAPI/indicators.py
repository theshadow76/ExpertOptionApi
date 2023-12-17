import numpy as np
from ExpertOptionAPI.expert import EoApi as ExpertAPI
import time
from ExpertOptionAPI._exceptions.Buying.BuyExceptions import BuyingExpirationInvalid

class _AlligatorIndicator:
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
            try:
                bot.Buy(amount=100, type="call", assetid=240, exptime=60, isdemo=1, strike_time=int(time.time()))
                return "Buy signal executed"
            except BuyingExpirationInvalid as e:
                print(f"A error ocured: {e}")
                attemps = 10
                for i in range(attemps):
                    try:
                        bot.Buy(amount=100, type="call", assetid=240, exptime=60, isdemo=1, strike_time=int(time.time()))
                        return "Buy succeded"
                    except Exception as e:
                        print(f"Another exception ocured: {e}")

        # Check for a sell signal (downward trend)
        if prev_order and not last_order:
            # Execute a sell order
            try:
                bot.Buy(amount=100, type="put", assetid=240, exptime=60, isdemo=1, strike_time=int(time.time()))
                return "Buy signal executed"
            except BuyingExpirationInvalid as e:
                print(f"A error ocured: {e}")
                attemps = 10
                for i in range(attemps):
                    try:
                        bot.Buy(amount=100, type="put", assetid=240, exptime=60, isdemo=1, strike_time=int(time.time()))
                        return "Sell succeded"
                    except Exception as e:
                        print(f"Another exception ocured: {e}")
        
        return "hold"

class _AssetAnalysis:
    def __init__(self, data):
        self.data = data['message']['candles']

    def calculate_percentages(self):
        percentages = []
        for candle in self.data:
            periods = candle['periods']
            for period in periods:
                open_price = period[1][0][0]
                close_price = period[1][-1][3]
                percentage_change = ((close_price - open_price) / open_price) * 100
                percentages.append(percentage_change)
        return percentages

    def calculate_rsi(self, periods=14):
            if len(self.data) < periods:
                return None  # Not enough data to compute RSI

            gains = []
            losses = []
            for i in range(1, periods + 1):
                change = self.data[i]['close'] - self.data[i - 1]['close']
                if change > 0:
                    gains.append(change)
                else:
                    losses.append(abs(change))

            average_gain = sum(gains) / periods
            average_loss = sum(losses) / periods if losses else 0

            if average_loss == 0:
                return 100  # Prevent division by zero

            rs = average_gain / average_loss
            rsi = 100 - (100 / (1 + rs))

            return rsi

    def check_overbought_oversold(self, rsi_thresholds=(70, 30)):
        overbought_threshold, oversold_threshold = rsi_thresholds
        rsi = self.calculate_rsi()

        if rsi is None:
            return None  # Not enough data

        if rsi > overbought_threshold:
            return "Overbought"
        elif rsi < oversold_threshold:
            return "Oversold"
        else:
            return "Neutral"


def AlligatorIndicatorTest(token, server_region):
    # << INIT ExpertAPI >>
    expert = ExpertAPI(token=token, server_region=server_region)
    expert.connect()

    # << LOOP >>
    for i in range(55550):
        # << GET DATA >>
        candles = expert.GetMultipleCandlesFromNow()

        # << Sample Usage >>
        alligator = _AlligatorIndicator(candles)
        market_status = alligator.evaluate_market(expert)
        print(market_status)
        time.sleep(5)

# Extract the close prices from the data
def extract_close_prices(data):
    close_prices = []
    for candle in data['message']['candles']:
        for period in candle['periods']:
            close_price = period[1][-1][3]  # Extract the closing price from each period
            close_prices.append({'close': close_price})
    return close_prices

def RelativeStrengthIndex(data):
    # Initialize the class with your data
    data_for_analysis = extract_close_prices(data)
    analysis = _AssetAnalysis(data_for_analysis)

    # Calculate the RSI
    rsi_value = analysis.calculate_rsi()
    # Check if the asset is overbought or oversold
    overbought_oversold_status = analysis.check_overbought_oversold()

    return {"RSI Value" : rsi_value, "Status" : overbought_oversold_status}