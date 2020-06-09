import logging
import random

from app.conf.settings import settings
from app.constants import Status
from app.database.base import connection_context
from app.database.models import Client, ClientTable, SmsMessage
from app.domain.sms.service import SendSmsService

from .datamodels import AuthServiceLoginResult, _Data, _Error

logger = logging.getLogger(__name__)


class AuthService:
    @classmethod
    def generate_random_code(cls) -> str:
        return ''.join(random.choice('0123456789') for _ in range(settings.code_length))

    @classmethod
    async def login(cls, phone: str) -> AuthServiceLoginResult:
        try:
            result = await cls._login(phone)
        except Exception:
            logger.exception('login unknown error')
            return AuthServiceLoginResult(status=Status.ERROR, error=_Error.UNKNOWN)
        else:
            return result

    @classmethod
    async def _login(cls, phone: str) -> AuthServiceLoginResult:
        async with connection_context() as conn:
            # send sms
            code = cls.generate_random_code()
            send_sms_result = await SendSmsService.send(phone, code)
            if send_sms_result.is_error:
                return AuthServiceLoginResult(status=Status.ERROR, error=_Error.CANT_SEND_SMS)

            # get or create client
            query = ClientTable.select().where(ClientTable.c.username == phone)
            result = await conn.execute(query)
            client = await result.fetchone()
            if not client:
                client = Client(username=phone)
                await client.save(conn)
                await client.refresh(conn)
            logger.info(client)

            # create sms msg in db
            msg = SmsMessage(
                provider_name=send_sms_result.data.provider_name,
                provider_message_id=send_sms_result.data.provider_message_id,
                code=code,
                client_id=client.id,
            )
            await msg.save(conn)
            await msg.refresh(conn)
            logger.info(msg)

        return AuthServiceLoginResult(status=Status.OK, data=_Data(client_id=client.id, msg_id=msg.id))
