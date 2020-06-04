from __future__ import annotations

import logging
from typing import Any, Optional

import aiohttp

from app.conf.settings import settings

logger = logging.getLogger(__name__)


# errors
class SmscClientError(Exception):
    pass


class IQSmsClient:
    _instance: Optional[IQSmsClient] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> IQSmsClient:
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
            f'{self.host}:{self.port}/messages/v2/send'
            f'?phone={phone}&text={text}&login={self.login}&password={self.password}'
        )
        logger.info(url)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                logger.info(resp.status)
                _id: str = await resp.text()
                logger.info(_id)
        return _id


iqsms_client = IQSmsClient(
    host=settings.iqsms.host,
    port=settings.iqsms.port,
    timeout=settings.iqsms.timeout,
    login=settings.iqsms.login,
    password=settings.iqsms.password,
)
