import datetime as dt
import logging
import random
from typing import Optional

import jwt
import jwt.exceptions
from passlib.context import CryptContext
from sqlalchemy import desc

from app.conf.settings import settings
from app.constants import Status, TokenType
from app.database.base import connection_context
from app.database.models import Client, ClientTable, SmsMessage, SmsMessageTable
from app.domain.sms.service import SendSmsService

from .datamodels import CheckCodeResult, CheckTokenResult, JWTPayload, SendCodeResult

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        is_ok: bool = pwd_context.verify(plain_password, hashed_password)
        return is_ok

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        password_hash: str = pwd_context.hash(password)
        return password_hash

    @classmethod
    def generate_random_code(cls) -> str:
        return ''.join(random.choice('0123456789') for _ in range(settings.code_length))

    @classmethod
    async def send_code(cls, username: str) -> SendCodeResult:
        try:
            result: SendCodeResult = await cls._send_code(username)
        except Exception:
            logger.exception('send_code unknown error')
            return SendCodeResult(status=Status.ERROR, error=SendCodeResult._Error.UNKNOWN)
        else:
            return result

    @classmethod
    async def check_code(cls, username: str, password: str) -> CheckCodeResult:
        try:
            result: CheckCodeResult = await cls._check_code(username, password)
        except Exception:
            logger.exception('check_code unknown error')
            return CheckCodeResult(status=Status.ERROR, error=CheckCodeResult._Error.UNKNOWN)
        else:
            return result

    @classmethod
    def check_token(cls, token: str) -> CheckTokenResult:
        try:
            raw_payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            jwt_payload = JWTPayload(**raw_payload)
        except jwt.exceptions.ExpiredSignatureError:
            return CheckTokenResult(status=Status.ERROR, error=CheckTokenResult._Error.EXPIRED)
        except Exception:
            logger.exception('jwt unknown error')
            return CheckTokenResult(status=Status.ERROR, error=CheckTokenResult._Error.UNKNOWN)
        return CheckTokenResult(status=Status.OK, jwt_payload=jwt_payload)

    @classmethod
    async def _send_code(cls, username: str) -> SendCodeResult:
        async with connection_context() as conn:
            # send sms
            code = cls.generate_random_code()
            logger.info(f'code: {code}')
            send_sms_result = await SendSmsService.send(username, code)
            if send_sms_result.is_error:
                return SendCodeResult(status=Status.ERROR, error=SendCodeResult._Error.CANT_SEND_SMS)

            # get or create client
            query = ClientTable.select().where(ClientTable.c.username == username)
            result = await conn.execute(query)
            client = await result.fetchone()
            if not client:
                client = Client(username=username)
                await client.save(conn)
                await client.refresh(conn)
            logger.info(client)

            # create sms msg in db
            msg = SmsMessage(
                provider_name=send_sms_result.data.provider_name,
                provider_message_id=send_sms_result.data.provider_msg_id,
                code=cls.get_password_hash(code),
                client_id=client.id,
            )
            await msg.save(conn)
            await msg.refresh(conn)
            logger.info(msg)
        return SendCodeResult(status=Status.OK, data=SendCodeResult._Data(client_id=client.id, msg_id=msg.id))

    @classmethod
    def _get_refresh_token(cls, username: str) -> Optional[str]:
        # generate refresh token
        exp = dt.datetime.utcnow() + dt.timedelta(days=settings.refresh_token_lifetime_in_days)
        jwt_payload = JWTPayload(username=username, type=TokenType.REFRESH, exp=exp)
        try:
            token = jwt.encode(jwt_payload.dict(), settings.jwt_secret, algorithm=settings.jwt_algorithm)
        except Exception:
            logger.exception('jwt unknown error')
            return None
        else:
            return token.decode('utf8')

    @classmethod
    def _get_access_token(cls, username: str) -> Optional[str]:
        # generate access token
        exp = dt.datetime.utcnow() + dt.timedelta(seconds=settings.access_token_lifetime_in_secs)
        jwt_payload = JWTPayload(username=username, type=TokenType.ACCESS, exp=exp)
        try:
            token = jwt.encode(jwt_payload.dict(), settings.jwt_secret, algorithm=settings.jwt_algorithm)
        except Exception:
            logger.exception('jwt unknown error')
            return None
        else:
            return token.decode('utf8')

    @classmethod
    async def _check_code(cls, username: str, password: str) -> CheckCodeResult:
        async with connection_context() as conn:
            # get  client
            query = ClientTable.select().where(ClientTable.c.username == username)
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
                return CheckCodeResult(status=Status.ERROR, error=CheckCodeResult._Error.SMS_MESSAGE_NOT_FOUND)
            if sms_message.used_at:
                return CheckCodeResult(status=Status.ERROR, error=CheckCodeResult._Error.CODE_WAS_USED)
            if not cls.verify_password(password, sms_message.code):
                return CheckCodeResult(status=Status.ERROR, error=CheckCodeResult._Error.INVALID_CODE)

            # generate token
            refresh_token = cls._get_refresh_token(username)
            access_token = cls._get_access_token(username)
            if not refresh_token or not access_token:
                return CheckCodeResult(status=Status.ERROR, error=CheckCodeResult._Error.UNKNOWN)

            query = (
                SmsMessageTable.update()
                .values(used_at=dt.datetime.utcnow())
                .where(SmsMessageTable.c.id == sms_message.id)
            )
            await conn.execute(query)

        return CheckCodeResult(
            status=Status.OK, data=CheckCodeResult._Data(refresh_token=refresh_token, access_token=access_token)
        )
