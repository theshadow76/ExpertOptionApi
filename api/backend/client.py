import simplejson as json
import logging

import websocket
import expoptapi.api.global_values as global_value
import pprint
from functools import partial
import pause

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
            "wss://fr24g1eu.expertoption.com/",     on_message=self.on_message,
    on_error=partial(self.on_error, self),
    on_close=partial(self.on_close, self),
    on_open=partial(self.on_open, self),
            # header=self.api.headers, cookie=self.api.cookie  # TODO test are they needed or not
        )
        self.token = token
    def on_message(self, message, *args, **kwargs):
        """Method to process websocket messages."""
        message = message.decode("utf-8")
        self.logger.info(f"Received message: {message}")
        self.latest_message = message  # Save the latest message

        message = json.loads(message)

        self.handle_action(message)
    def handle_action(self, message):
        action = message.get('action')
        ns = message.get('ns')
        self.logger.info(f"Action is: {action}")

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

    def on_open(self, wss, *args, **kwargs):  # pylint: disable=unused-argument
        """Method to process websocket open."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Websocket client connected. Args: {args}")
        logger.debug("Websocket client connected.")
        global_value.check_websocket_if_connect = 1

        data2 = {
            "action": "setContext",
            "message": {
                "is_demo": 1
            },
            "token": self.token,
            "ns": 1
        }


        data = {
            "action": "multipleAction",
            "msg": {
                "token": self.token,
                "v": 18,
                "action": "multipleAction",
                "message": {
                    "token": self.token,
                    "actions": [
                        {"action": "getCountries", "message": None, "ns": None, "v": 18, "token": self.token},
                        {"action": "getCurrency", "message": None, "ns": None, "v": 18, "token": self.token},
                        {"action": "profile", "message": None, "ns": None, "v": 18, "token": self.token},
                        {"action": "environment", "message": None, "ns": None, "v": 18, "token": self.token},
                        {
                            "action": "assets",
                            "message": {"mode": ["vanilla", "binary"], "subscribeMode": ["vanilla"]},
                            "ns": None,
                            "v": 18,
                            "token": self.token,
                        },
                        {"action": "openOptions", "message": None, "ns": None, "v": 18, "token": self.token},
                        {"action": "userGroup", "message": None, "ns": None, "v": 18, "token": self.token},
                        {
                            "action": "setTimeZone",
                            "message": {"timeZone": 360},
                            "ns": None,
                            "v": 18,
                            "token": self.token,
                        },
                        {"action": "historySteps", "message": None, "ns": None, "v": 18, "token": self.token},
                        {
                            "action": "tradeHistory",
                            "message": {"mode": ["binary", "vanilla"], "count": 100, "index_from": 0},
                            "ns": None,
                            "v": 18,
                            "token": self.token,
                        },
                    ],
                },
            },
            "ns": "_common",
        }

        self.wss.send(json.dumps(data2))
        logger.info(f"Sent first data: {data2}")
        pause.seconds(3)
        # self.wss.send(json.dumps(data))
        # logger.info(f"Sent first data: {data}")

    def on_close(self, *args, **kwargs):  # pylint: disable=unused-argument
        """Method to process websocket close."""
        logger = logging.getLogger(__name__)
        logger.debug("Websocket connection closed.")
        logger.debug(f"Websocket connection closed. Args: {args}")
        try:
            self.logger.warning("Trying to reconnect from close")
            v1 = self.api.connect()
            if v1:
                self.logger.info("Sucess!")
            else:
                self.logger.critical("A error ocured when reconecting")
        except Exception as e:
            self.logger.error(f"A error ocured: {e}")
        global_value.check_websocket_if_connect = 0