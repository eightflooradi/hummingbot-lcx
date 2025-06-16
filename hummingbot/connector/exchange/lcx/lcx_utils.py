from decimal import Decimal
from typing import Any, Dict

from pydantic import ConfigDict, Field, SecretStr

from hummingbot.client.config.config_data_types import BaseConnectorConfigMap
from hummingbot.core.data_type.trade_fee import TradeFeeSchema

CENTRALIZED = True

EXAMPLE_PAIR = "ETH-USDT"

DEFAULT_FEES = TradeFeeSchema(
    maker_percent_fee_decimal=Decimal("0.002"),
    taker_percent_fee_decimal=Decimal("0.002"),
)


def is_exchange_information_valid(exchange_info: Dict[str, Any]) -> bool:
    return True


class LCXConfigMap(BaseConnectorConfigMap):
    connector: str = "lcx"
    lcx_api_key: SecretStr = Field(
        default=..., 
        json_schema_extra={
            "prompt": "Enter your LCX API key",
            "is_secure": True,
            "is_connect_key": True,
            "prompt_on_new": True,
        }
    )
    lcx_secret_key: SecretStr = Field(
        default=..., 
        json_schema_extra={
            "prompt": "Enter your LCX secret key",
            "is_secure": True,
            "is_connect_key": True,
            "prompt_on_new": True,
        }
    )

    model_config = ConfigDict(title="lcx")


KEYS = LCXConfigMap.model_construct()
