from expoptapi.api.backend.client import WebSocketClient
import asyncio
import logging
from collections import defaultdict, OrderedDict
from threading import Thread
import threading
import ssl
import time
import simplejson as json
import pause


class EoApi:
    def __init__(self, token: str, server_region):
        self.token = token
        self.server_region = server_region

        self.websocket_client = WebSocketClient(api=self, token=self.token)  # Composition
        self.logger = logging.getLogger(__name__)

        self.websocket_thread = None
        self.ping_thread = None
        self.profile = None
        self.message_callback = None
        self._request_id = 1
        self.results = self.FixSizeOrderedDict(max=300)
        self.msg_by_ns = self.FixSizeOrderedDict(max=300)
        self.msg_by_action = self.nested_dict(1, lambda: self.FixSizeOrderedDict(max=300))

    async def Profile(self):
        self.logger.info("Fetching profile")
        profile = self.profile
        latest_message = self.websocket_client.latest_message
        return {"Profile": f"{profile}", "LatestMessage": latest_message}

    def connect(self):
        # implementation similar to the ExpertOptionAPI class...
        pass

    def auto_ping(self):
        # implementation similar to the ExpertOptionAPI class...
        pass

    def send_websocket_request(self, action: str, msg, ns: str = None):
        # implementation similar to the ExpertOptionAPI class...
        pass

    # Other methods similar to ExpertOptionAPI...
    def nested_dict(self, n, type):
        if n == 1:
            return defaultdict(type)
        else:
            return defaultdict(lambda: self.nested_dict(n - 1, type))

    class FixSizeOrderedDict(OrderedDict):
        def __init__(self, *args, max=0, **kwargs):
            self._max = max
            super().__init__(*args, **kwargs)

        def __setitem__(self, key, value):
            OrderedDict.__setitem__(self, key, value)
            if self._max > 0:
                if len(self) > self._max:
                    self.popitem(False)

    @property
    def request_id(self):
        self._request_id += 1
        return str(self._request_id - 1)

    # ... (Add other methods and properties that you need)

class _api:
    def __init__(self, token: str) -> None:
        self.token = token

    def _profile(self):

        # Assuming WebSocketClient is set up to handle this data
        # WebSocket loop should probably not be here.
        # You should start it in your main function or some entry point.
        return {"Response": "Success"}
