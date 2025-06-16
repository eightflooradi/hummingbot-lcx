from hummingbot.connector.exchange.lcx import lcx_constants as CONSTANTS
from hummingbot.core.api_throttler.throttler import Throttler
from hummingbot.core.web_assistant.web_assistants_factory import WebAssistantsFactory


def public_rest_url(path_url: str) -> str:
    return f"{CONSTANTS.REST_URL}/{path_url}"


def private_rest_url(path_url: str) -> str:
    return f"{CONSTANTS.REST_URL}/{path_url}"


def build_api_factory(throttler: Throttler, time_synchronizer, auth=None) -> WebAssistantsFactory:
    return WebAssistantsFactory(throttler=throttler, auth=auth, time_synchronizer=time_synchronizer)
