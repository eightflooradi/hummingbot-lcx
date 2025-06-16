import hashlib
import hmac
import base64
import json
from urllib.parse import urlparse
from typing import Any, Dict

from hummingbot.connector.exchange.lcx import lcx_constants as CONSTANTS
from hummingbot.connector.time_synchronizer import TimeSynchronizer
from hummingbot.core.web_assistant.auth import AuthBase
from hummingbot.core.web_assistant.connections.data_types import RESTRequest, WSRequest


class LCXAuth(AuthBase):
    """Authenticates REST and WebSocket requests to the LCX exchange."""

    def __init__(self, api_key: str, secret_key: str, time_provider: TimeSynchronizer):
        self._api_key = api_key
        self._secret_key = secret_key
        self._time_provider = time_provider

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def secret_key(self) -> str:
        return self._secret_key

    async def rest_authenticate(self, request: RESTRequest) -> RESTRequest:
        ts = str(int(self._time_provider.time() * 1e3))
        parsed = urlparse(request.url)
        endpoint = parsed.path
        payload = request.data if request.data is not None else {}
        payload_str = json.dumps(payload) if payload != "" else json.dumps(payload)
        request_string = f"{request.method}{endpoint}{payload_str}"
        sign_bytes = hmac.new(self._secret_key.encode(), request_string.encode(), hashlib.sha256).digest()
        signature = base64.b64encode(sign_bytes).decode()
        headers = request.headers or {}
        headers.update(
            {
                "x-access-key": self._api_key,
                "x-access-sign": signature,
                "x-access-timestamp": ts,
                "API-VERSION": CONSTANTS.API_VERSION,
            }
        )
        request.headers = headers
        return request

    async def ws_authenticate(self, request: WSRequest) -> WSRequest:
        return request
