import simplejson as json
import logging
import random
import websocket
import ExpertOptionAPI.api.global_values as global_value
import pprint
from functools import partial
import pause
from ExpertOptionAPI.api.constants import REGION
import threading
import ssl
from ExpertOptionAPI._exceptions.Buying.BuyExceptions import BuyingExpirationInvalid

class WebSocketClient:
    def __init__(self, api, token):
        """
        :param api: The instance of :class:`ExpertOptionAPI
            <expertoption.api.ExpertOptionAPI>`.
        """
        self.api = api
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

        # Create file handler and add it to the logger
        file_handler = logging.FileHandler('expert.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.latest_message = None  # To store the latest message
        self.wss = websocket.WebSocketApp(
            "wss://fr24g1eu.expertoption.com/",     on_message=self.on_message,
    on_error=self.on_error,
    on_close=self.on_close,
    on_open=self.on_open
            # header=self.api.headers, cookie=self.api.cookie  # TODO test are they needed or not
        )
        self.token = token
    def reconnect(self):
        # List of regions to try
        REG = REGION()
        regions = REG.get_regions()

        for region in regions:
            try:
                self.logger.info(f"Attempting to reconnect to {region}")
                self.wss = websocket.WebSocketApp(
                    region,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open
                )
                # Here you might want to establish the connection
                # Depending on how your WebSocketApp is set up, you might need to start a new thread or use `run_forever`
                self.websocket_thread = threading.Thread(target=self.wss.run_forever, kwargs={
                    'sslopt': {
                        "check_hostname": False,
                        "cert_reqs": ssl.CERT_NONE,
                        "ca_certs": "cacert.pem"
                    },
                    "ping_interval": 0,
                    'skip_utf8_validation': True,
                    "origin": "https://app.expertoption.com",
                    # "http_proxy_host": '127.0.0.1', "http_proxy_port": 8890
                })

                self.websocket_thread.daemon = True
                self.websocket_thread.start()
                break  # Break the loop if connection is successful
            except Exception as e:
                self.logger.error(f"Failed to connect to {region}: {str(e)}")
                continue  # Try the next region
    def on_message(self, ws, message, *args, **kwargs):
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
            global_value.CandlesData = message
        if action == "buyOption" and global_value.is_buy == True:
            global_value.BuyData = message
            print(message)
        if action == "candles":
            global_value.CandlesData = message
        if action == "assetHistoryCandles":
            global_value.SingleCandleData = message
            print(f"The assetHistoryCandles data is: {message}")
        if action == "error":
            global_value.ErrorData = message
            print(f"A error ocured: {message}")
            if "ERROR_EXPIRATION_INVALID" in message:
                raise BuyingExpirationInvalid()
        if action == "subscribeCandles":
            global_value.SingleCandleData = message
            print(f"The subscribe candles data is: {message}")

        else:
            print(f"Unknown action: {action}")

    def on_error(self, error, *args, **kwargs):  # pylint: disable=unused-argument
        """Method to process websocket errors."""
        logger = logging.getLogger(__name__)
        logger.error(f"WebSocket error: {error}, Args: {args}, Kwargs: {kwargs}")
        global_value.check_websocket_if_connect = -1
        self.reconnect()

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
        self.reconnect()