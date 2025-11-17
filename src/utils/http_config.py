import aiohttp
from src.utils.log import setup_logger
logger = setup_logger(__name__, "http_setup.log")

import aiohttp
import logging

logger = logging.getLogger(__name__)

async def on_request_start(session, trace_config_ctx, params):
    logger.debug("=== REQUEST SENT ===")
    logger.debug(f"METHOD: {params.method}")
    logger.debug(f"URL: {params.url}")
    logger.debug(f"HEADERS: {params.headers}")

    # Cookies
    cookie_header = params.headers.get("Cookie")
    logger.debug(f"COOKIES SENT: {cookie_header}")

    # Content-Type
    content_type = params.headers.get("Content-Type")
    logger.debug(f"CONTENT-TYPE SENT: {content_type}")

    # # Body: must log manually from your request_kwargs
    # request_body = getattr(trace_config_ctx, "request_body", "<not provided>")
    # logger.debug(f"BODY SENT: {request_body}")


async def on_request_end(session, trace_config_ctx, params):
    logger.debug("=== RESPONSE RECEIVED ===")
    logger.debug(f"STATUS: {params.response.status}")
    logger.debug(f"RESPONSE HEADERS: {params.response.headers}")
    logger.debug(f"RESPONSE CONTENT-TYPE: {params.response.headers.get('Content-Type')}")


# Attach trace config
trace_config = aiohttp.TraceConfig()
trace_config.on_request_start.append(on_request_start)
trace_config.on_request_end.append(on_request_end)

 #on_request_prepare is required to capture request body because aiohttp does not expose it in params directly.



class HttpConfig:
    _instance = None
    _session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def get_session(self):
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)

            #Adjusting the TCP Connector may yield different performance levels in production
            connector = aiohttp.TCPConnector(limit=60, limit_per_host=40)


            self._session = aiohttp.ClientSession(
                trace_configs=[trace_config],
                timeout=timeout,
                connector=connector
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None  # reset so it can be recreated

http_client = HttpConfig()