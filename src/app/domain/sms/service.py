import random

from app.client import smsc_client, stream_telecom_client


class SendSmsService:
    @classmethod
    async def send(cls, phone: str, text: str) -> str:
        _client = random.choice([smsc_client, stream_telecom_client])
        _id = await _client.send(phone, text)
        return _id
