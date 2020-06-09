import logging
import random

from app.client import iqsms_client, smsc_client, stream_telecom_client
from app.constants import SmsProvider, Status

from .datamodels import SendSmsServiceResult, _Data, _Error

SMS_PROVIDER_MAP = {
    SmsProvider.IQSMS: iqsms_client,
    SmsProvider.SMSC: smsc_client,
    SmsProvider.STREAM_TELECOM: stream_telecom_client,
}

logger = logging.getLogger(__name__)


class SendSmsService:
    @classmethod
    async def send(cls, phone: str, text: str) -> SendSmsServiceResult:
        sms_provider_name = random.choice(list(SmsProvider))
        try:
            _id = '1234'
            # await SMS_PROVIDER_MAP[sms_provider_name].send(phone, text)
        except Exception:
            return SendSmsServiceResult(status=Status.ERROR, error=_Error.UNKNOWN)
        else:
            return SendSmsServiceResult(
                status=Status.OK, data=_Data(provider_name=sms_provider_name, provider_msg_id=_id)
            )
