import logging
import random

import jwt
from sqlalchemy import desc

from app.conf.settings import settings
from app.constants import Status
from app.database.base import connection_context
from app.database.models import Client, ClientTable, SmsMessage, SmsMessageTable
from app.domain.sms.service import SendSmsService

from .datamodels import CheckCodeResult, SendCodeResult

logger = logging.getLogger(__name__)


class AuthService:
    @classmethod
    def generate_random_code(cls) -> str:
        return ''.join(random.choice('0123456789') for _ in range(settings.code_length))

    @classmethod
    async def send_code(cls, phone: str) -> SendCodeResult:
        try:
            result: SendCodeResult = await cls._send_code(phone)
        except Exception:
            logger.exception('send_code unknown error')
            return SendCodeResult(status=Status.ERROR, error=SendCodeResult._Error.UNKNOWN)
        else:
            return result

    @classmethod
    async def check_code(cls, phone: str, password: str) -> CheckCodeResult:
        try:
            result: CheckCodeResult = await cls._check_code(phone, password)
        except Exception:
            logger.exception('check_code unknown error')
            return CheckCodeResult(status=Status.ERROR, error=CheckCodeResult._Error.UNKNOWN)
        else:
            return result

    @classmethod
    async def _send_code(cls, phone: str) -> SendCodeResult:
        async with connection_context() as conn:
            # send sms
            code = cls.generate_random_code()
            send_sms_result = await SendSmsService.send(phone, code)
            if send_sms_result.is_error:
                return SendCodeResult(status=Status.ERROR, error=SendCodeResult._Error.CANT_SEND_SMS)

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
                provider_message_id=send_sms_result.data.provider_msg_id,
                code=code,
                client_id=client.id,
            )
            await msg.save(conn)
            await msg.refresh(conn)
            logger.info(msg)
        return SendCodeResult(status=Status.OK, data=SendCodeResult._Data(client_id=client.id, msg_id=msg.id))

    @classmethod
    async def _check_code(cls, phone: str, password: str) -> CheckCodeResult:
        async with connection_context() as conn:
            # get  client
            query = ClientTable.select().where(ClientTable.c.username == phone)
            result = await conn.execute(query)
            client = await result.fetchone()
            if not client:
                return CheckCodeResult(status=Status.ERROR, error=CheckCodeResult._Error.CLIENT_NOT_FOUND)

            # get sms_message
            query = (
                SmsMessageTable.select()
                .where(SmsMessageTable.c.client_id == client.id)
                .order_by(desc(SmsMessageTable.c.created_at))
            )
            result = await conn.execute(query)
            sms_message = await result.fetchone()
            if not sms_message:
                return CheckCodeResult(status=Status.ERROR, error=CheckCodeResult._Error.SMS_MESSAGE_FOUND)
            if sms_message.code != password:
                return CheckCodeResult(status=Status.ERROR, error=CheckCodeResult._Error.INVALID_CODE)

            # generate token
            try:
                token = jwt.encode({'phone': phone}, settings.jwt_sectet, algorithm=settings.jwt_algorithm)
            except Exception:
                logger.exception('jwt unknown error')
                return CheckCodeResult(status=Status.ERROR, error=CheckCodeResult._Error.UNKNOWN)

        return CheckCodeResult(status=Status.OK, data=CheckCodeResult._Data(token=token.decode('utf8')))
