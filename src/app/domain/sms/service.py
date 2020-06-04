from .client import sms_client


class SendSmsService:
    @classmethod
    async def send(cls, phone: str, text: str) -> str:
        _id = await sms_client.send(phone, text)
        return _id
