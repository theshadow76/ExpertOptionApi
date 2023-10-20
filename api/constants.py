class REGION:
    EUROPE = "wss://fr24g1eu.expertoption.com/"
    INDIA = "wss://fr24g1in.expertoption.com/"
    HONG_KONG = "wss://fr24g1hk.expertoption.com/"
    SINGAPORE = "wss://fr24g1sg.expertoption.com/"
    UNITED_STATES = "wss://fr24g1us.expertoption.com/"

class Symbols:
    EURUSD = 0

class BasicData:
    def __init__(self, token) -> None:
        self.token = token
    def SendData(self):
        BasicSendData = {"token": self.token, "v": 18, "action": "multipleAction",
                                         "message": {"token": self.token, "actions": [
                                             {"action": "getCountries", "message": None, "ns": None, "v": 18,
                                              "token": self.token},
                                             {"action": "getCurrency", "message": None, "ns": None, "v": 18,
                                              "token": self.token},
                                             {"action": "profile", "message": None, "ns": None, "v": 18,
                                              "token": self.token},
                                             {"action": "environment", "message": None, "ns": None, "v": 18,
                                              "token": self.token}, {"action": "assets",
                                                                     "message": {"mode": ["vanilla", "binary"],
                                                                                 "subscribeMode": ["vanilla"]},
                                                                     "ns": None, "v": 18, "token": self.token},
                                             {"action": "openOptions", "message": None, "ns": None, "v": 18,
                                              "token": self.token},
                                             {"action": "userGroup", "message": None, "ns": None, "v": 18,
                                              "token": self.token},
                                             {"action": "setTimeZone", "message": {"timeZone": 360}, "ns": None,
                                              "v": 18, "token": self.token},
                                             {"action": "historySteps", "message": None, "ns": None, "v": 18,
                                              "token": self.token}, {"action": "tradeHistory",
                                                                     "message": {"mode": ["binary", "vanilla"],
                                                                                 "count": 100, "index_from": 0},
                                                                     "ns": None, "v": 18, "token": self.token}]}}
        return BasicSendData
    def BuyData(self, amount, type, assetid, exptime, isdemo, strike_time):
        data = {"action":"buyOption","message":{"type": type,"amount": amount,"assetid": assetid,"strike_time":strike_time,"expiration_time": exptime,"is_demo": isdemo,"rateIndex":1},"token": self.token,"ns":300}
        return data