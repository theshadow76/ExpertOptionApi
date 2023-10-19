"""Module for base ExpertOption base websocket chanel."""


class Base(object):
    """Class for base ExpertOption websocket chanel."""

    # pylint: disable=too-few-public-methods

    add_token: bool = True

    def __init__(self, api):
        """
        :param api: The instance of :class:`ExpertOptionAPI
            <expertoptionapi.api.ExpertOptionAPI>`.
        """
        self.api = api

    def send_websocket_request(self, action, msg, ns=None):
        """Send request to ExpertOption server websocket.

        :param str action: The websocket chanel name.
        :param dict msg: The websocket chanel msg.

        :returns: The instance of :class:`requests.Response`.
        """

        if self.add_token:
            msg['token'] = self.api.token

        return self.api.send_websocket_request(action, msg, ns=ns)
