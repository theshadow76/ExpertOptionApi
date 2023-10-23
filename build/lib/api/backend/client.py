import simplejson as json
import logging

import websocket
import api.global_values as global_value
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
    on_error=self.on_error,
    on_close=self.on_close,
    on_open=self.on_open
            # header=self.api.headers, cookie=self.api.cookie  # TODO test are they needed or not
        )
        self.token = token
    def on_message(self, message, *args, **kwargs):
        """Method to process websocket messages."""
        message = message.decode('utf-8')
        self.logger.info(f"Received message: {message}")
        self.latest_message = message  # Save the latest message

        message = json.loads(message)

        self.handle_action(message)
    def handle_action(self, message):
        action = message.get('action')
        ns = message.get('ns')
        is_profile = global_value.is_profile
        self.logger.info(f"Action is: {action}")
        if action == "multipleAction":
            for sub_message in message['message']['actions']:
                self.handle_action(sub_message)  # recursively handle each action

        if action == "userGroup" and global_value.is_UserGroup == True:
            # handle userGroup action
            print("Handling userGroup")

        if action == "profile" and global_value.is_profile == True:
            global_value.ProfileData = message

        if action == "assets" and global_value.is_assets == True:
            global_value.AssetsData = message

        if action == "getCurrency" and global_value.is_GetCurrency == True:
            # handle getCurrency action
            print("Handling getCurrency")

        if action == "getCountries" and global_value.is_GetCurrencies == True:
            # handle getCountries action
            print("Handling getCountries")

        if action == "environment" and global_value.is_enviroment == True:
            # handle environment action
            print("Handling environment")

        if action == "SubscribeCandles" and global_value.is_SubscribeCandles == True:
            # handle defaultSubscribeCandles action
            print("Handling defaultSubscribeCandles")

        if action == "getCandlesTimeframes" and global_value.is_GetCandles_timeFrames == True:
            # handle getCandlesTimeframes action
            print("Handling getCandlesTimeframes")
        if action == "buyOption" and global_value.is_buy == True:
            global_value.BuyData = message
            print(message)

        else:
            print(f"Unknown action: {action}")

    def on_error(self, error):  # pylint: disable=unused-argument
        """Method to process websocket errors."""
        logger = logging.getLogger(__name__)
        logger.error(error)
        global_value.check_websocket_if_connect = -1

    def on_open(self, *args, **kwargs):  # pylint: disable=unused-argument
        """Method to process websocket open."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Websocket client connected. Args: {args}")
        logger.debug("Websocket client connected.")
        global_value.check_websocket_if_connect = 1
    def on_close(self, *args, **kwargs):  # pylint: disable=unused-argument
        """Method to process websocket close."""
        logger = logging.getLogger(__name__)
        logger.debug("Websocket connection closed.")
        logger.debug(f"Websocket connection closed. Args: {args}")
        global_value.check_websocket_if_connect = 0