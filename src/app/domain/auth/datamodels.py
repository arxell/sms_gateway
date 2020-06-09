from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app.datamodels import MyResultModel


class JWTPayload(BaseModel):
    username: str


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
        token: str

    error: Optional[_Error]
    data: Optional[_Data]
