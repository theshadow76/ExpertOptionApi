import simplejson as json
import logging

import websocket
import expoptapi.api.global_values as global_value
import pprint
from functools import partial

class WebSocketClient:
    def __init__(self, api, token):
        """
        :param api: The instance of :class:`ExpertOptionAPI
            <expertoption.api.ExpertOptionAPI>`.
        """
        self.api = api
        self.logger = logging.getLogger(__name__)
        self.latest_message = None  # To store the latest message
        self.wss = websocket.WebSocketApp(
            "wss://fr24g1eu.expertoption.com/ws/v34?app_os=mac&app_source=web&app_type=web&app_version=13.0.6&app_build_number=3977&app_brand=expertoption&app_device_info=",     on_message=partial(self.on_message, self),
    on_error=partial(self.on_error, self),
    on_close=partial(self.on_close, self),
    on_open=partial(self.on_open, self),
            # header=self.api.headers, cookie=self.api.cookie  # TODO test are they needed or not
        )
        self.token = token
        self.wss.run_forever()
    def on_message(self, message):
        """Method to process websocket messages."""
        self.logger.debug(f"Received message: {message}")
        message = message.decode('utf-8')
        self.latest_message = message  # Save the latest message

        message = json.loads(message)

        self.handle_action(message)
    def handle_action(self, message):
        action = message.get('action')
        ns = message.get('ns')

        if action == "multipleAction":
            for sub_message in message['message']['actions']:
                self.handle_action(sub_message)  # recursively handle each action

        elif action == "userGroup":
            # handle userGroup action
            print("Handling userGroup")

        elif action == "profile":
            # handle profile action
            print("Handling profile")

        elif action == "assets":
            # handle assets action
            print("Handling assets")

        elif action == "getCurrency":
            # handle getCurrency action
            print("Handling getCurrency")

        elif action == "getCountries":
            # handle getCountries action
            print("Handling getCountries")

        elif action == "environment":
            # handle environment action
            print("Handling environment")

        elif action == "defaultSubscribeCandles":
            # handle defaultSubscribeCandles action
            print("Handling defaultSubscribeCandles")

        elif action == "setTimeZone":
            # handle setTimeZone action
            print("Handling setTimeZone")

        elif action == "getCandlesTimeframes":
            # handle getCandlesTimeframes action
            print("Handling getCandlesTimeframes")

        else:
            print(f"Unknown action: {action}")

    def on_error(self, error):  # pylint: disable=unused-argument
        """Method to process websocket errors."""
        logger = logging.getLogger(__name__)
        logger.error(error)
        global_value.check_websocket_if_connect = -1

    def on_open(self, wss, *args):  # pylint: disable=unused-argument
        """Method to process websocket open."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Websocket client connected. Args: {args}")
        logger.debug("Websocket client connected.")
        global_value.check_websocket_if_connect = 1

        data = {
            "action": "multipleAction",
            "message": {
                "actions": [
                    {"action": "userGroup", "ns": 1, "token": self.token},
                    {"action": "profile", "ns": 2, "token": self.token},
                    {"action": "assets", "message": {"mode": ["vanilla"], "subscribeMode": ["vanilla"]}, "ns": 3, "token": self.token},
                    {"action": "getCurrency", "ns": 4, "token": self.token},
                    {"action": "getCountries", "ns": 5, "token": self.token},
                    {"action": "environment", "ns": 6, "token": self.token},
                    {"action": "defaultSubscribeCandles", "message": {"modes": ["vanilla"], "timeframes": [0, 5]}, "ns": 7, "token": self.token},
                    {"action": "setTimeZone", "message": {"timeZone": -180}, "ns": 8, "token": self.token},
                    {"action": "getCandlesTimeframes", "ns": 9, "token": self.token},
                ]
            },
            "token": self.token,
            "ns": 212  # Some namespace value, if applicable
        }
        self.wss.send(json.dumps(data))

    def on_close(self, *args):  # pylint: disable=unused-argument
        """Method to process websocket close."""
        logger = logging.getLogger(__name__)
        logger.debug("Websocket connection closed.")
        logger.debug(f"Websocket connection closed. Args: {args}")
        global_value.check_websocket_if_connect = 0