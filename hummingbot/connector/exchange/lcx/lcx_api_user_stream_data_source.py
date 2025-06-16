import asyncio
import hmac
import base64
import hashlib
from typing import TYPE_CHECKING, List

from hummingbot.connector.exchange.lcx import lcx_constants as CONSTANTS
from hummingbot.connector.exchange.lcx.lcx_auth import LCXAuth
from hummingbot.core.data_type.user_stream_tracker_data_source import UserStreamTrackerDataSource
from hummingbot.core.web_assistant.web_assistants_factory import WebAssistantsFactory
from hummingbot.core.web_assistant.ws_assistant import WSAssistant
from hummingbot.core.web_assistant.connections.data_types import WSJSONRequest

if TYPE_CHECKING:
    from hummingbot.connector.exchange.lcx.lcx_exchange import LCXExchange


class LCXAPIUserStreamDataSource(UserStreamTrackerDataSource):
    def __init__(self, auth: LCXAuth, trading_pairs: List[str], connector: 'LCXExchange', api_factory: WebAssistantsFactory):
        super().__init__()
        self._auth = auth
        self._trading_pairs = trading_pairs
        self._connector = connector
        self._api_factory = api_factory

    async def _connected_websocket_assistant(self) -> WSAssistant:
        ws: WSAssistant = await self._api_factory.get_ws_assistant()
        ts = str(int(self._connector._time_synchronizer.time() * 1e3))
        sign_bytes = hmac.new(self._auth.secret_key.encode(), ts.encode(), hashlib.sha256).digest()
        signature = base64.b64encode(sign_bytes).decode()
        url = f"{CONSTANTS.WSS_PRIVATE_URL}?x-access-key={self._auth.api_key}&x-access-sign={signature}&x-access-timestamp={ts}"
        await ws.connect(ws_url=url, ping_timeout=CONSTANTS.PING_TIMEOUT)
        return ws

    async def _subscribe_channels(self, websocket_assistant: WSAssistant):
        payloads = [
            {"Topic": "subscribe", "Type": "user_orders"},
            {"Topic": "subscribe", "Type": "user_wallets"},
        ]
        for payload in payloads:
            await websocket_assistant.send(WSJSONRequest(payload=payload))
