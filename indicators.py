

class RSI:
    def __init__(self) -> None:
        # NOTE: The data are the list of closes, if you use the Expert Option API as your data provider, you'll get the last item in each list (close)
        self.data = None # data are the candles
        # NOTE: THe avarage gain and loss will be accessible in the json `trades.json`
        self.average_gain = None # average_gain is the avarage wins you do, let's say you made 10 trades, and you won 7 of them, each trade you invested 1 USD, this would mean you made wrothly 7 usd (depends), so that mean your average_gain is 7
        self.average_loss = None # Same here, average_loss is the amount of looses you get, in this case 3 USD
        # NOTE: So this means when calculating the rsi, you'll do: RSI¹ = 100-(100/(1+(average gain / average loss)))
        self.previous_average_gain = None
        self.previous_average_loss = None
    def calculate(self, data, perdiods):
        """ Calculate RSI data """
        self.data = data

        # Check if the period is 13 or lower
        if perdiods <= 13:
            # do RSI for 13 or less periods
            # here we will do the folowing formula: RSI¹ = 100-(100/(1+(average gain / average loss)))
            rsi1 = 100 - (100 / (1 + (self.average_gain / self.average_loss)))
            return rsi1 # And here we return this
        # If the period is over 14
        else:
            # we do the folowing formula: RSI² = 100-(100/(1+((previous average gain * 13 + current gain)/(previous average loss * 13 + current loss))))
            rsi2 = 100 - (100 / (1 + ((self.previous_average_gain * 13 + self.average_gain) / (self.previous_average_loss * 13 + self.average_loss))))
            return rsi2




