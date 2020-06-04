import random

from app.client import iqsms_client, smsc_client, stream_telecom_client
from app.constants import SmsProvider
from app.database.base import connection_context
from app.database.models import SmsMessage

SMS_PROVIDER_MAP = {
    SmsProvider.IQSMS: iqsms_client,
    SmsProvider.SMSC: smsc_client,
    SmsProvider.STREAM_TELECOM: stream_telecom_client,
}


class SendSmsService:
    @classmethod
    async def send(cls, phone: str, text: str) -> str:
        sms_provider_name = random.choice(list(SmsProvider))
        _id = await SMS_PROVIDER_MAP[sms_provider_name].send(phone, text)

        async with connection_context() as conn:
            await SmsMessage(provider_name=sms_provider_name, provider_message_id=_id).save(conn)
        return _id
