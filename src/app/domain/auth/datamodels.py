import datetime as dt
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app.constants import TokenType
from app.datamodels import MyResultModel


class JWTPayload(BaseModel):
    username: str
    type: TokenType
    exp: Optional[dt.datetime]

    # @property
    # def is_expired(self) -> bool:
    #     if self.exp and dt.datetime.utcnow() >= self.exp:
    #         return True
    #     return False


class SendCodeResult(MyResultModel):
    class _Error(str, Enum):
        CANT_SEND_SMS = 'CANT_SEND_SMS'
        UNKNOWN = 'UNKNOWN'

    class _Data(BaseModel):
        client_id: int
        msg_id: int

    error: Optional[_Error]
    data: Optional[_Data]


class CheckCodeResult(MyResultModel):
    class _Error(str, Enum):
        UNKNOWN = 'UNKNOWN'
        CLIENT_NOT_FOUND = 'CLIENT_NOT_FOUND'
        SMS_MESSAGE_NOT_FOUND = 'SMS_MESSAGE_NOT_FOUND'
        INVALID_CODE = 'INVALID_CODE'

    class _Data(BaseModel):
        refresh_token: str
        access_token: str

    error: Optional[_Error]
    data: Optional[_Data]


class CheckTokenResult(MyResultModel):
    class _Error(str, Enum):
        UNKNOWN = 'UNKNOWN'
        EXPIRED = 'EXPIRED'

    error: Optional[_Error]
    jwt_payload: Optional[JWTPayload]

    @property
    def is_error_expired(self) -> bool:
        return self.error == self._Error.EXPIRED
