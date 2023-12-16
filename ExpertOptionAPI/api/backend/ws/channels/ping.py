"""Module for ExpertOption ping websocket chanel."""
from ExpertOptionAPI.api.backend.ws.channels.base import Base


class Ping(Base):
    """Class for Binary ping websocket chanel."""

    action = "ping"

    def __call__(self, ns: str = None, json=False):
        """Method to send message to ping websocket chanel.
        """

        data = {
            "action": self.action,
            "v": 23,
            "message": {},
        }

        if json:
            return data
        else:
            return self.send_websocket_request(self.action, data, ns=ns or "_")
