import datetime as dt

from sqlalchemy import Column, DateTime, Enum, Integer, String

from app.constants import SmsProvider

from .base import ModelBase


class SmsMessage(ModelBase):
    __tablename__ = "sms_message"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(Enum(SmsProvider), nullable=False, create_type=False)
    provider_message_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)

    def __str__(self) -> str:
        return f'{self.id} {self.provider_name} {self.provider_message_id}'
