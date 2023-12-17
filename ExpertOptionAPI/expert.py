# Made by © Vigo Walker

from ExpertOptionAPI.api.backend.client import WebSocketClient
import asyncio
import logging
from collections import defaultdict, OrderedDict
from threading import Thread
import threading
import ssl
import time
import simplejson as json
import pause
import websocket
import decimal
import urllib
from websocket._exceptions import WebSocketConnectionClosedException
import datetime

from ExpertOptionAPI._exceptions.Buying.BuyExceptions import BuyingExpirationInvalid

from ExpertOptionAPI.api.backend.ws.channels.ping import Ping


import ExpertOptionAPI.api.global_values as global_value
from ExpertOptionAPI.api.constants import BasicData, Symbols

class EoApi:
    def __init__(self, token: str, server_region = None, *args, **kwargs):
        self.token = token
        self.server_region = server_region
        self.utli = _Utils()

        self.websocket_client = WebSocketClient(api=self, token=self.token)  # Composition
        # Set logging level and format
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

        # Create file handler and add it to the logger
        file_handler = logging.FileHandler('expert.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)


        self.logger.info("Initializing EoApi with token: %s, region: %s", token, server_region)

        self.websocket_thread = None
        self.profile = None
        self.message_callback = None
        self._request_id = 1
        self.results = self.FixSizeOrderedDict(max=300)
        self.msg_by_ns = self.FixSizeOrderedDict(max=300)
        self.msg_by_action = self.nested_dict(1, lambda: self.FixSizeOrderedDict(max=300))

        self.ping_thread = threading.Thread(target=self.auto_ping)  # Create a new thread for auto_ping
        self.ping_thread.daemon = True  # Set the thread as a daemon so it will terminate when the main program terminates
        self.ping_thread.start()  # Start the auto_ping thread

        # self.websocket_client.wss.run_forever()

    def Profile(self):
        self.logger.info("Fetching profile")
        global_value.is_profile = True
        self.send_websocket_request(action="multipleAction",
                                    msg=BasicData.SendData(self),
                                    ns="_common")
        return global_value.ProfileData
    def GetCandles(self):
        data =  {"action":"subscribeCandles","message":{"assets":[{"id":142,"timeframes":[0,5]}],"modes":["vanilla"]},"token":self.token,"ns":18}
        global_value.is_GetCandles_timeFrames = True
        self.send_websocket_request(action="subscribeCandles", msg=data)
        return global_value.CandlesData
    def GetCandlesHistory(self, periods: int = time.time()):
        # Starting interval of 300 seconds
        base_interval = 300

        # Initialize the list to store the periods
        desired_periods = []

        # Calculate the periods, incrementing the interval each time
        for i in range(10):
            if i < 9:  # For the first nine periods, add 127 seconds each time
                round_interval = base_interval + i * 127
            else:  # For the last period, add 83 seconds instead
                round_interval = base_interval + i * 127 + 83

            # Calculate the rounded timestamp
            rounded_timestamp = self.utli.roundTimeToLastTimestamp(dt=None, roundTo=round_interval)

            # Add the period to the list
            desired_periods.append([rounded_timestamp, rounded_timestamp + round_interval])

        # Update data with the new periods
        data = {
            "action": "assetHistoryCandles",
            "message": {
                "assetid": 240,
                "periods": desired_periods,
                "timeframes": [0]  # Adjusted as per your requirement
            },
            "token": self.token,  # Ensure this is the correct token
            "ns": 11
        }
        print(data)
        global_value.is_GetassetHistoryCandles = True
        self.send_websocket_request(action="assetHistoryCandles", msg=data)
        return global_value.assetHistoryCandles

    def Buy(self, amount: int = 1, type: str = "call", assetid: int = 240, exptime: int = 60, isdemo: int = 1, strike_time: int = int(time.time())):
    # Your method implementation here
        try:
            self.logger.info("Buying...")
            print("Buying...") # replace in prod
            if isdemo == 1:
                self.SetDemo()
            exptime_ = self.utli.roundTimeToTimestamp(dt=None, roundTo=exptime)
            print(f"The exp_time is: {int(exptime_)}")
            try:
                self.send_websocket_request(action="BuyOption", msg={"action":"buyOption","message":{"type":f"{type}","amount":amount,"assetid":assetid,"strike_time":strike_time,"expiration_time":int(exptime_),"is_demo":isdemo,"rateIndex":1},"token":f"{self.token}","ns":44})
                return global_value.BuyData
            except BuyingExpirationInvalid as e:
                for i in range(15):
                    exp_time_v2 = self.utli.roundTimeToTimestamp(dt=None, roundTo=60)
                    self.send_websocket_request(action="BuyOption", msg={"action":"buyOption","message":{"type":f"{type}","amount":amount,"assetid":assetid,"strike_time":strike_time,"expiration_time":int(exp_time_v2),"is_demo":isdemo,"rateIndex":1},"token":f"{self.token}","ns":44})
                    try:
                        time.sleep(10)
                        return global_value.BuyData
                    except BuyingExpirationInvalid as e2:
                        print(f"Still got the error: {e2}")
        except WebSocketConnectionClosedException as e:
            print(f"Error: {e}")
            self.websocket_client.wss.close()
            self.connect()
            self.logger.info("Buying...")
            print("Buying...") # replace in prod
            self.send_websocket_request(action="BuyOption", msg=BasicData.BuyData(self=self, amount=amount, type=type, assetid=assetid, exptime=exptime, isdemo=isdemo, strike_time=strike_time), ns=300)
            return global_value.BuyData
    def SetDemo(self):
        data = {"action":"setContext","message":{"is_demo":1},"token": self.token,"ns":1}
        self.send_websocket_request(action="setContext", msg=data, ns="_common")
        return True
    def GetSingleCandles(self):
        # Starting interval of 300 seconds
        base_interval = 300

        # Initialize the list to store the periods
        desired_periods = []

        # Calculate the periods, incrementing the interval each time
        for i in range(2):
            if i < 9:  # For the first nine periods, add 127 seconds each time
                round_interval = base_interval + i * 127
            else:  # For the last period, add 83 seconds instead
                round_interval = base_interval + i * 127 + 83

            # Calculate the rounded timestamp
            rounded_timestamp = self.utli.roundTimeToLastTimestamp(dt=None, roundTo=round_interval)

            # Add the period to the list
            desired_periods.append([rounded_timestamp, rounded_timestamp + round_interval])
        data = {"action":"assetHistoryCandles","message":{"assetid":240,"periods":desired_periods,"timeframes":[5]},"token":self.token,"ns":27}
        self.send_websocket_request(action="assetHistoryCandles", msg=data)
        return global_value.SingleCandleData
    
    def GetMultipleCandlesFromNow(self):
        # Starting interval of 300 seconds
        base_interval = 120

        # Initialize the list to store the periods
        desired_periods = []

        # Calculate the periods, incrementing the interval each time
        for i in range(10):
            if i < 9:  # For the first nine periods, add 127 seconds each time
                round_interval = base_interval + i * 127
            else:  # For the last period, add 83 seconds instead
                round_interval = base_interval + i * 127 + 87

            # Calculate the rounded timestamp
            rounded_timestamp = self.utli.roundTimeToLastTimestamp(dt=None, roundTo=round_interval)

            # Add the period to the list
            desired_periods.append([rounded_timestamp, rounded_timestamp + round_interval])
        data = {"action":"assetHistoryCandles","message":{"assetid":240,"periods":desired_periods,"timeframes":[5]},"token":self.token,"ns":27}
        self.send_websocket_request(action="assetHistoryCandles", msg=data)
        return global_value.SingleCandleData

    def connect(self):
        global_value.check_websocket_if_connect = None

        self.websocket_client = WebSocketClient(self, token=self.token)

        self.websocket_thread = threading.Thread(target=self.websocket_client.wss.run_forever, kwargs={
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

        # self.authorize(authorize=self.token)

        # TODO support it
        # self.multiple_action(actions=[
        #     self.get_countries(json=True),
        #     self.get_currency(json=True),
        #     self.get_profile(json=True),
        #     self.get_environment(json=True),
        #     self.get_open_options(json=True),
        #     self.get_user_group(json=True),
        #     self.get_set_time_zone(json=True),
        #     self.get_history_steps(json=True),
        #     self.get_trade_history(json=True),
        # ], ns="_common")

        self.websocket_client.wss.keep_running = True

        while True:
            try:
                if global_value.check_websocket_if_connect == 0 or global_value.check_websocket_if_connect == -1:
                    return False
                elif global_value.check_websocket_if_connect == 1:
                    break
            except Exception:
                pass
            pass

        self.send_websocket_request(action="multipleAction",
                                    msg={"token": self.token, "v": 18, "action": "multipleAction",
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
                                                                     "ns": None, "v": 18, "token": self.token}]}},
                                    ns="_common")
        data = {
                "action": "multipleAction",
                "message": {
                    "actions": [
                        {
                            "action": "userGroup",
                            "ns": 1,
                            "token": self.token
                        },
                        {
                            "action": "profile",
                            "ns": 2,
                            "token": self.token
                        },
                        {
                            "action": "assets",
                            "message": {
                                "mode": ["vanilla"],
                                "subscribeMode": ["vanilla"]
                            },
                            "ns": 3,
                            "token": self.token
                        },
                        {
                            "action": "getCurrency",
                            "ns": 4,
                            "token": self.token
                        },
                        {
                            "action": "getCountries",
                            "ns": 5,
                            "token": self.token
                        },
                        {
                            "action": "environment",
                            "ns": 6,
                            "token": self.token
                        },
                        {
                            "action": "defaultSubscribeCandles",
                            "message": {
                                "modes": ["vanilla"],
                                "timeframes": [0, 5]
                            },
                            "ns": 7,
                            "token": self.token
                        },
                        {
                            "action": "setTimeZone",
                            "message": {
                                "timeZone": -180
                            },
                            "ns": 8,
                            "token": self.token
                        },
                        {
                            "action": "getCandlesTimeframes",
                            "ns": 9,
                            "token": self.token
                        }
                    ]
                },
                "token": self.token,
                "ns": 2
            }
        
        data2 = {
            "action": "multipleAction",
            "message": {
                "actions": [
                    {
                        "action": "openOptions",
                        "ns": 1,
                        "token": self.token
                    },
                    {
                        "action": "tradeHistory",
                        "message": {"index_from": 0, "count": 20, "is_demo": 1},
                        "ns": 2,
                        "token": self.token
                    },
                    {
                        "action": "tradeHistory",
                        "message": {"index_from": 0, "count": 20, "is_demo": 0},
                        "ns": 3,
                        "token": self.token
                    },
                    {
                        "action": "getTournaments",
                        "ns": 4,
                        "token": self.token
                    },
                    {
                        "action": "getTournamentInfo",
                        "ns": 5,
                        "token": self.token
                    }
                ]
            },
            "token": self.token,
            "ns": 4
        }

        self.SetDemo()

        self.send_websocket_request(action="multipleAction", msg=data2)

        self.send_websocket_request(action="multipleAction", msg=data)

        start_t = time.time()
        self.logger.info("WebSocket connected")
        return True
    def auto_ping(self):
        self.logger.info("Starting auto ping thread")

        while True:
            pause.seconds(5)  # Assuming that you've imported 'pause'
            try:
                if self.websocket_client.wss.sock and self.websocket_client.wss.sock.connected:  # Check if socket is connected
                    self.ping()
                else:
                    self.logger.warning("WebSocket is not connected. Attempting to reconnect.")
                    # Attempt reconnection
                    if self.connect():
                        self.logger.info("Successfully reconnected.")
                    else:
                        self.logger.warning("Reconnection attempt failed.")
                    try:
                        self.ping()
                        self.logger.info("Sent ping reuqests successfully!")
                    except Exception as e:
                        self.logger.error(f"A error ocured trying to send ping: {e}")
            except Exception as e:  # Catch exceptions and log them
                self.logger.error(f"An error occurred while sending ping or attempting to reconnect: {e}")
                try:
                    self.logger.warning("Trying again...")
                    v1 = self.connect()
                    if v1:
                        self.logger.info("Conection completed!, sending ping...")
                        self.ping()
                    else:
                        self.logger.error("Connection was not established")
                except Exception as e:
                    self.logger.error(f"A error ocured when trying again: {e}")

            pause.seconds(5)  # Assuming that you've imported 'pause'


    def send_websocket_request(self, action: str, msg, ns: str = None):
        """Send websocket request to ExpertOption server.
        :type action: str
        :param ns: str
        :param dict msg: The websocket request msg.
        """
        self.logger.debug("Sending WebSocket request: action=%s, ns=%s", action, ns)

        if ns is not None and not ns:
            ns = self.request_id

        msg['ns'] = ns

        if ns:
            # self.results[ns] = None
            self.msg_by_ns[ns] = None
            self.msg_by_action[action][ns] = None

        def default(obj):
            if isinstance(obj, decimal.Decimal):
                return str(obj)
            raise TypeError

        data = json.dumps(msg, default=default)
        self.logger.debug(data)

        self.websocket_client.wss.send(bytearray(urllib.parse.quote(data).encode('utf-8')), opcode=websocket.ABNF.OPCODE_BINARY)
        pause.seconds(5)
        return ns

    def nested_dict(self, n, type):
        if n == 1:
            return defaultdict(type)
        else:
            return defaultdict(lambda: self.nested_dict(n - 1, type))
    @property
    def request_id(self):
        self._request_id += 1
        return str(self._request_id - 1)

    @property
    def ping(self):
        self.logger.info("Sent a ping request")
        return Ping(self).__call__

    class FixSizeOrderedDict(OrderedDict):
        def __init__(self, *args, max=0, **kwargs):
            self._max = max
            super().__init__(*args, **kwargs)

        def __setitem__(self, key, value):
            OrderedDict.__setitem__(self, key, value)
            if self._max > 0:
                if len(self) > self._max:
                    self.popitem(False)


class _api:
    def __init__(self, token: str) -> None:
        self.token = token

    def _profile(self):

        # Assuming WebSocketClient is set up to handle this data
        # WebSocket loop should probably not be here.
        # You should start it in your main function or some entry point.
        return {"Response": "Success"}

class _Utils:
    def __init__(self) -> None:
        pass
    def roundTimeToTimestamp(self, dt=None, roundTo=60):
        """Round a datetime object to any time lapse in seconds and return Unix timestamp
        dt : datetime.datetime object, default now.
        roundTo : Closest number of seconds to round to, default 1 minute.
        """
        if dt == None: 
            dt = datetime.datetime.now()
        seconds = (dt.replace(tzinfo=None) - dt.min).seconds
        rounding = (seconds + roundTo / 2) // roundTo * roundTo
        rounded_dt = dt + datetime.timedelta(0, rounding - seconds, -dt.microsecond)
        return rounded_dt.timestamp()
    def roundTimeToLastTimestamp(self, dt=None, roundTo=60):
        """Round a datetime object down to any time lapse in seconds and return Unix timestamp
        dt : datetime.datetime object, default now.
        roundTo : Number of seconds to round down to, default 1 minute.
        """
        if dt == None: 
            dt = datetime.datetime.now()
        seconds = (dt.replace(tzinfo=None) - dt.min).seconds
        rounding = seconds // roundTo * roundTo
        rounded_dt = dt - datetime.timedelta(seconds=seconds - rounding, microseconds=dt.microsecond)
        return int(rounded_dt.timestamp())

