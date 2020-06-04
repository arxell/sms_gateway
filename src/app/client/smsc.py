from __future__ import annotations

import logging
from typing import Any, Optional

import aiohttp

from app.conf.settings import settings

logger = logging.getLogger(__name__)


# errors
class SmscClientError(Exception):
    pass


class SmscClient:
    _instance: Optional[SmscClient] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> SmscClient:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host: str, port: int, timeout: float, login: str, password: str) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.login = login
        self.password = password

    async def send(self, phone: str, text: str) -> str:
        url = (
            f'{self.host}:{self.port}/sys/send.php'
            f'?login={self.login}&psw={self.password}&phones={phone}>&mes={text}'
        )
        logger.info(url)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                logger.info(resp.status)
                _id: str = await resp.text()
                logger.info(_id)
        return _id


smsc_client = SmscClient(
    host=settings.smsc.host,
    port=settings.smsc.port,
    timeout=settings.smsc.timeout,
    login=settings.smsc.login,
    password=settings.smsc.password,
)
