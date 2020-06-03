from __future__ import annotations

import logging
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


# errors
class SmsClientError(Exception):
    pass


class SmsClient:
    _instance: Optional[SmsClient] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> SmsClient:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host: str, port: int, timeout: float) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.user_name = 'SMS Info'
        self.login = '79636351616'
        self.password = 'oCcOwbecOK'

    async def send(self, phone: str, text: str) -> str:
        url = (
            f'{self.host}:{self.port}/get/'
            f'?user={self.login}&pwd={self.password}&sadr={self.user_name}&dadr={phone}&text={text}'
        )
        logger.info(url)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                logger.info(resp.status)
                _id = await resp.text()
                logger.info(_id)
        return _id


sms_client = SmsClient(host='http://gateway.api.sc', port=80, timeout=3)
