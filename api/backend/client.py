import asyncio
import logging
import websockets
import simplejson as json

class WebsocketClient:
    def __init__(self, api):
        self.server = "wss://fr24g1eu.expertoption.com/ws/v34?app_os=mac&app_source=web&app_type=web&app_version=13.0.5&app_build_number=3850&app_brand=expertoption&app_device_info"
        self.loop = asyncio.get_event_loop()

    async def send_receive(self, data):
        async with websockets.connect(self.server) as websocket:
            await websocket.send(data)
            response = await websocket.recv()
            return response

    def send_receive_sync(self, data):
        return self.loop.run_until_complete(self.send_receive(data))

    def on_message(self, message):
        logger = logging.getLogger(__name__)
        message = json.loads(message)
        logger.debug(message)

        self.handle_action(message)


    def start(self, data):
        response = self.send_receive_sync(data)
        self.on_message(response)
