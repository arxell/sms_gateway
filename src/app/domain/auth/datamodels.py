from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app.datamodels import MyModel


class SendCodeResult(MyModel):
    class _Error(str, Enum):
        CANT_SEND_SMS = 'CANT_SEND_SMS'
        UNKNOWN = 'UNKNOWN'

    class _Data(BaseModel):
        client_id: int
        msg_id: int

    error: Optional[_Error]
    data: Optional[_Data]


class CheckCodeResult(MyModel):
    class _Error(str, Enum):
        UNKNOWN = 'UNKNOWN'
        CLIENT_NOT_FOUND = 'CLIENT_NOT_FOUND'
        SMS_MESSAGE_FOUND = 'SMS_MESSAGE_FOUND'
        INVALID_CODE = 'INVALID_CODE'

    class _Data(BaseModel):
        token: str

    error: Optional[_Error]
    data: Optional[_Data]
