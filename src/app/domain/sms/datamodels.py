from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app.constants import SmsProvider
from app.datamodels import MyResultModel


class _Error(str, Enum):
    UNKNOWN = 'UNKNOWN'


class _Data(BaseModel):
    provider_name: SmsProvider
    provider_msg_id: str


class SendSmsServiceResult(MyResultModel):
    error: Optional[_Error]
    data: Optional[_Data]
