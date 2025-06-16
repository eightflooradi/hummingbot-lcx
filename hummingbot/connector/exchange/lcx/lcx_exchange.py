from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from hummingbot.connector.constants import s_decimal_NaN
from hummingbot.connector.exchange.lcx import (
    lcx_constants as CONSTANTS,
    lcx_utils,
    lcx_web_utils as web_utils,
)
from hummingbot.connector.exchange.lcx.lcx_api_order_book_data_source import LCXAPIOrderBookDataSource
from hummingbot.connector.exchange.lcx.lcx_api_user_stream_data_source import LCXAPIUserStreamDataSource
from hummingbot.connector.exchange.lcx.lcx_auth import LCXAuth
from hummingbot.connector.exchange_py_base import ExchangePyBase
from hummingbot.core.data_type.common import OrderType, TradeType
from hummingbot.core.data_type.order_book_tracker_data_source import OrderBookTrackerDataSource
from hummingbot.core.data_type.trade_fee import AddedToCostTradeFee
from hummingbot.core.data_type.user_stream_tracker_data_source import UserStreamTrackerDataSource
from hummingbot.core.web_assistant.connections.data_types import RESTMethod
from hummingbot.core.web_assistant.web_assistants_factory import WebAssistantsFactory

if TYPE_CHECKING:
    from hummingbot.client.config.config_helpers import ClientConfigAdapter


class LCXExchange(ExchangePyBase):
    """Connector for trading on the LCX centralized exchange."""

    web_utils = web_utils

    def __init__(
        self,
        client_config_map: "ClientConfigAdapter",
        lcx_api_key: str,
        lcx_secret_key: str,
        trading_pairs: Optional[List[str]] = None,
        trading_required: bool = True,
    ):
        self._api_key = lcx_api_key
        self._secret_key = lcx_secret_key
        self._trading_pairs = trading_pairs
        self._trading_required = trading_required
        super().__init__(client_config_map=client_config_map)

    @property
    def authenticator(self):
        return LCXAuth(api_key=self._api_key, secret_key=self._secret_key, time_provider=self._time_synchronizer)

    @property
    def name(self) -> str:
        return "lcx"

    @property
    def rate_limits_rules(self):
        return CONSTANTS.RATE_LIMITS

    @property
    def domain(self):
        return CONSTANTS.DEFAULT_DOMAIN

    @property
    def client_order_id_max_length(self):
        return CONSTANTS.MAX_ORDER_ID_LEN

    @property
    def client_order_id_prefix(self):
        return CONSTANTS.HBOT_ORDER_ID_PREFIX

    @property
    def trading_rules_request_path(self):
        return CONSTANTS.GET_TRADING_RULES_PATH_URL

    @property
    def trading_pairs_request_path(self):
        return CONSTANTS.GET_TRADING_RULES_PATH_URL

    @property
    def check_network_request_path(self):
        return CONSTANTS.CHECK_NETWORK_PATH_URL

    @property
    def trading_pairs(self):
        return self._trading_pairs

    @property
    def is_cancel_request_in_exchange_synchronous(self) -> bool:
        return True

    @property
    def is_trading_required(self) -> bool:
        return self._trading_required

    def supported_order_types(self) -> List[OrderType]:
        return [OrderType.LIMIT, OrderType.MARKET]

    async def _place_order(
        self,
        order_id: str,
        trading_pair: str,
        amount: Decimal,
        trade_type: TradeType,
        order_type: OrderType,
        price: Decimal,
        **kwargs
    ) -> Tuple[str, float]:
        symbol = await self.exchange_symbol_associated_to_pair(trading_pair)
        side = "BUY" if trade_type is TradeType.BUY else "SELL"
        data: Dict[str, Any] = {
            "Pair": symbol,
            "Amount": float(amount),
            "OrderType": "LIMIT" if order_type.is_limit_type() else "MARKET",
            "Side": side,
        }
        if order_type.is_limit_type():
            data["Price"] = float(price)
        rest_assistant = await self._web_assistants_factory.get_rest_assistant()
        resp = await rest_assistant.execute_request(
            url=web_utils.private_rest_url(CONSTANTS.CREATE_ORDER_PATH_URL),
            method=RESTMethod.POST,
            data=data,
            is_auth_required=True,
        )
        exchange_order_id = str(resp.get("data", {}).get("Id"))
        timestamp = resp.get("data", {}).get("CreatedAt", self.current_timestamp)
        return exchange_order_id, float(timestamp)

    async def _place_cancel(self, order_id: str, tracked_order):
        symbol = await self.exchange_symbol_associated_to_pair(tracked_order.trading_pair)
        params = {"orderId": tracked_order.exchange_order_id or order_id}
        rest_assistant = await self._web_assistants_factory.get_rest_assistant()
        await rest_assistant.execute_request(
            url=web_utils.private_rest_url(CONSTANTS.CANCEL_ORDER_PATH_URL),
            method=RESTMethod.DELETE,
            params=params,
            is_auth_required=True,
        )
        return True

    def _create_web_assistants_factory(self) -> WebAssistantsFactory:
        return web_utils.build_api_factory(
            throttler=self._throttler, time_synchronizer=self._time_synchronizer, auth=self._auth
        )

    def _create_order_book_data_source(self) -> OrderBookTrackerDataSource:
        return LCXAPIOrderBookDataSource(
            trading_pairs=self._trading_pairs, connector=self, api_factory=self._web_assistants_factory
        )

    def _create_user_stream_data_source(self) -> UserStreamTrackerDataSource:
        return LCXAPIUserStreamDataSource(
            auth=self._auth, trading_pairs=self._trading_pairs, connector=self, api_factory=self._web_assistants_factory
        )

    def _get_fee(
        self,
        base_currency: str,
        quote_currency: str,
        order_type: OrderType,
        order_side: TradeType,
        amount: Decimal,
        price: Decimal = s_decimal_NaN,
        is_maker: Optional[bool] = None,
    ) -> AddedToCostTradeFee:
        is_maker = order_type is OrderType.LIMIT_MAKER
        return AddedToCostTradeFee(percent=self.estimate_fee_pct(is_maker))
