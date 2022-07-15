try:
    from micropython import const

    upy = True
except ImportError:
    const = lambda x: x
    upy = False


class Application:
    """An application registered on `pushover.org`."""

    URL_BASE = "https://api.pushover.net"
    API_VERSION = "1"

    def __init__(self, app_token: str, user_token: "str | None" = None):
        """Initialise a new application."""
        self.app_token = app_token
        self.user_token = user_token
        self.notification_params = {}

    def notification(self, **kwargs) -> "Notification":
        """Get a new Notification object."""
        if not self.user_token:
            raise ValueError("No user token set.")
        kwargs |= self.notification_params
        return Notification(self, **kwargs)

    def _sync_request(
        self,
        method: str,
        url: str,
        params: "dict | None" = None,
        data: "dict | None" = None,
    ) -> dict:
        if upy:
            import urequests as requests
        else:
            import requests
        resp = requests.request(method, url, params=params, data=data)
        resp.raise_for_status()
        return resp.json()

    async def _async_request(
        self,
        method: str,
        url: str,
        params: "dict | None" = None,
        data: "dict | None" = None,
    ) -> dict:
        if upy:
            import uaiohttpclient as aiohttp
        else:
            import aiohttp
        async with aiohttp.ClientSession() as session:
            resp = await session.request(method, url, params=params, data=data)
            resp.raise_for_status()
            return await resp.json()

    @property
    def message_endpoint(self) -> str:
        """Full url to the messages endpoint."""
        return f"{self.URL_BASE}/{self.API_VERSION}/messages.json"

    def receipt_endpoint(self, receipt: str) -> str:
        """Full url to the receipts endpoint."""
        return f"{self.URL_BASE}/{self.API_VERSION}/receipts/{receipt}.json"

    def _add_tokens(self, **kwargs):
        data = dict(token=self.app_token, user=self.user_token)
        return data | kwargs

    def _sync_push_msg(self, **kwargs):
        return self._sync_request(
            "post", self.message_endpoint, data=self._add_tokens(**kwargs)
        )

    async def _async_push_msg(self, **kwargs):
        return await self._async_request(
            "post", self.message_endpoint, data=self._add_tokens(**kwargs)
        )


class Notification:
    """A notification, whether sent or not."""

    UNSENT = 0
    SENT = 1
    ERRORED = 2

    LOWEST_PRIORITY = -2
    LOW_PRIORITY = -1
    NORMAL_PRIORITY = 0
    HIGH_PRIORITY = 1
    EMERGENCY_PRIORITY = 2

    def __init__(
        self,
        app: Application,
        **kwargs,
    ):
        """Initialise a new notification."""
        self.payload = dict(
            sound="bugle",
            retry=60,
            expire=3600,
        )
        self.payload |= kwargs
        self.receipt = None
        self._last_poll = None
        self.app = app
        self._state = self.UNSENT

    @property
    def state(self):
        """Notification state."""
        return self._state

    def _set_receipt(self, resp: dict) -> None:
        if self.payload.get("priority") == self.EMERGENCY_PRIORITY:
            self.receipt = resp["receipt"]

    def send(self):
        """Send a message."""
        resp = self.app._sync_push_msg(**self.payload)
        self._set_receipt(resp)
        self._state = self.SENT

    async def async_send(self):
        """Send a message."""
        resp = await self.app._async_push_msg(**self.payload)
        self._set_receipt(resp)
        self._state = self.SENT
