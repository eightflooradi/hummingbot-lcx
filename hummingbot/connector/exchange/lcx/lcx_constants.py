from hummingbot.core.api_throttler.data_types import RateLimit
from hummingbot.core.data_type.in_flight_order import OrderState

EXCHANGE_NAME = "lcx"
REST_URL = "https://exchange-api.lcx.com"
WSS_PUBLIC_URL = "wss://exchange-api.lcx.com/ws"
WSS_PRIVATE_URL = "wss://exchange-api.lcx.com/api/auth/ws"
PING_TIMEOUT = 20

DEFAULT_DOMAIN = ""
MAX_ORDER_ID_LEN = 32
HBOT_ORDER_ID_PREFIX = "HBOT"
API_VERSION = "1.1.0"

# REST API ENDPOINTS
CHECK_NETWORK_PATH_URL = "api/pairs"
GET_TRADING_RULES_PATH_URL = "api/pairs"
GET_LAST_TRADING_PRICES_PATH_URL = "api/tickers"
GET_ORDER_BOOK_PATH_URL = "api/book"
CREATE_ORDER_PATH_URL = "api/create"
CANCEL_ORDER_PATH_URL = "api/cancel"
GET_ACCOUNT_SUMMARY_PATH_URL = "api/balances"
GET_ORDER_DETAIL_PATH_URL = "api/order"
GET_TRADE_DETAIL_PATH_URL = "api/uHistory"
SERVER_TIME_PATH = "api/pairs"

RATE_LIMITS = [
    RateLimit(limit_id="MARKET", limit=25, time_interval=1),
    RateLimit(limit_id="TRADING", limit=5, time_interval=1),
    RateLimit(limit_id="TRADING_MINUTE", limit=90, time_interval=60),
]

ORDER_STATE = {
    "OPEN": OrderState.OPEN,
    "CLOSED": OrderState.FILLED,
    "CANCEL": OrderState.CANCELED,
    "PARTIAL": OrderState.PARTIALLY_FILLED,
}
