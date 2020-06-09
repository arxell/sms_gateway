from enum import Enum
from typing import Optional

from app.datamodels import MyModel


class _Error(str, Enum):
    CANT_SEND_SMS = 'CANT_SEND_SMS'
    UNKNOWN = 'UNKNOWN'


class _Data(str, Enum):
    client_id: int
    msg_id: int


class AuthServiceLoginResult(MyModel):
    error: Optional[_Error]
    data: Optional[_Data]
