import asyncio
import logging
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

logger = logging.getLogger(__name__)


class SendSmsService:
    @classmethod
    async def send(cls, phone: str, text: str) -> str:
        sms_provider_name = random.choice(list(SmsProvider))
        delay = random.randint(100, 300) / 1000
        await asyncio.sleep(delay)
        # _id = await SMS_PROVIDER_MAP[sms_provider_name].send(phone, text)
        _id = '123'

        async with connection_context() as conn:
            msg = SmsMessage(provider_name=sms_provider_name, provider_message_id=_id)
            await msg.save(conn)
            await msg.refresh(conn)
            logger.info(msg)
        return _id
