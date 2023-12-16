from ExpertOptionAPI.api.backend.client import WebSocketClient
from ExpertOptionAPI.api.constants import REGION

class ExpertProfile:
    def __init__(self, token: str):
        self.action = "profile"
        self.message_type = "call"
        self.amount = 25
        self.assetid = 240
        self.strike_time = 1697554336
        self.expiration_time = 1697554345
        self.is_demo = 1
        self.rateIndex = 1
        self.ns = None
        self.token = token

    async def get(self):
        europe = REGION.EUROPE
        data = {"action": "profile", "message": None, "ns": None, "v": 18,
                                              "token": self.token}
        client = WebSocketClient(api=self.api)