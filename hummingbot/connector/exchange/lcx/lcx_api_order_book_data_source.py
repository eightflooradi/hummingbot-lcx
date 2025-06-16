import asyncio
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from hummingbot.connector.exchange.lcx import lcx_constants as CONSTANTS, lcx_web_utils as web_utils
from hummingbot.core.data_type.order_book_message import OrderBookMessage, OrderBookMessageType
from hummingbot.core.data_type.order_book_tracker_data_source import OrderBookTrackerDataSource
from hummingbot.core.web_assistant.connections.data_types import RESTMethod
from hummingbot.core.web_assistant.web_assistants_factory import WebAssistantsFactory

if TYPE_CHECKING:
    from hummingbot.connector.exchange.lcx.lcx_exchange import LCXExchange


class LCXAPIOrderBookDataSource(OrderBookTrackerDataSource):
    def __init__(self, trading_pairs: List[str], connector: 'LCXExchange', api_factory: WebAssistantsFactory):
        super().__init__(trading_pairs)
        self._connector = connector
        self._api_factory = api_factory

    async def get_last_traded_prices(self, trading_pairs: List[str], domain: Optional[str] = None) -> Dict[str, float]:
        result: Dict[str, float] = {}
        rest_assistant = await self._api_factory.get_rest_assistant()
        for trading_pair in trading_pairs:
            symbol = await self._connector.exchange_symbol_associated_to_pair(trading_pair)
            url = web_utils.public_rest_url(CONSTANTS.GET_LAST_TRADING_PRICES_PATH_URL)
            params = {"pair": symbol}
            data = await rest_assistant.execute_request(url=url, params=params, method=RESTMethod.GET)
            price = float(data.get("data", {}).get("lastPrice", "nan"))
            result[trading_pair] = price
        return result

    async def listen_for_order_book_diffs(self, ev_loop: asyncio.AbstractEventLoop, output: asyncio.Queue):
        raise NotImplementedError

    async def listen_for_order_book_snapshots(self, ev_loop: asyncio.AbstractEventLoop, output: asyncio.Queue):
        raise NotImplementedError

    async def _order_book_snapshot(self, trading_pair: str) -> OrderBookMessage:
        rest_assistant = await self._api_factory.get_rest_assistant()
        symbol = await self._connector.exchange_symbol_associated_to_pair(trading_pair)
        url = web_utils.public_rest_url(CONSTANTS.GET_ORDER_BOOK_PATH_URL)
        params = {"pair": symbol}
        data = await rest_assistant.execute_request(url=url, params=params, method=RESTMethod.GET)
        ts = self._connector.current_timestamp
        content = {
            "trading_pair": trading_pair,
            "update_id": int(ts * 1e3),
            "bids": data.get("data", {}).get("buy", []),
            "asks": data.get("data", {}).get("sell", []),
        }
        return OrderBookMessage(OrderBookMessageType.SNAPSHOT, content, timestamp=ts)
