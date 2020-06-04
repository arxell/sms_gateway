from __future__ import annotations

import logging
from typing import Any, Optional

import aiohttp

from app.conf.settings import settings

logger = logging.getLogger(__name__)


# errors
class StreamTelecomClientError(Exception):
    pass


class StreamTelecomClient:
    _instance: Optional[StreamTelecomClient] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> StreamTelecomClient:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host: str, port: int, timeout: float, username: str, login: str, password: str) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.username = username
        self.login = login
        self.password = password

    async def send(self, phone: str, text: str) -> str:
        url = (
            f'{self.host}:{self.port}/get/'
            f'?user={self.login}&pwd={self.password}&sadr={self.username}&dadr={phone}&text={text}'
        )
        logger.info(url)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                logger.info(resp.status)
                _id: str = await resp.text()
                logger.info(_id)
        return _id


stream_telecom_client = StreamTelecomClient(
    host=settings.stream_telecom.host,
    port=settings.stream_telecom.port,
    timeout=settings.stream_telecom.timeout,
    username=settings.stream_telecom.username,
    login=settings.stream_telecom.login,
    password=settings.stream_telecom.password,
)
