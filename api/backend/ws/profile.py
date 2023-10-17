from expoptapi.api.backend.client import MainClient

class ExpertProfile:
    def __init__(self):
        self.action = "setContext"
        self.message_type = "call"
        self.amount = 25
        self.assetid = 240
        self.strike_time = 1697554336
        self.expiration_time = 1697554345
        self.is_demo = 1
        self.rateIndex = 1
        self.ns = 180

    async def get(self, token):
        data = f"""
        {{
            "action": "{self.action}",
            "message": {{
                "is_demo": {self.is_demo}
            }},
            "token": "{token}",
            "ns": {self.ns}
        }}
        """
        GetProfile = MainClient(server="wss://fr24g1eu.expertoption.com/ws/v34?app_os=mac&app_source=web&app_type=web&app_version=13.0.5&app_build_number=3850&app_brand=expertoption&app_device_info=", data=data)
        return await GetProfile