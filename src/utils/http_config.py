import aiohttp
class HttpConfig:
    _instance = None
    _session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def get_session(self, headers:dict=None):
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)

            #Adjusting the TCP Connector may yield different performance levels in production
            connector = aiohttp.TCPConnector(limit=60, limit_per_host=40)


            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=connector
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None  # reset so it can be recreated

http_client = HttpConfig()