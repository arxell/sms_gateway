from sqlalchemy import Column, Enum, Integer, String

from app.constants import SmsProvider

from .base import ModelBase


class SmsMessage(ModelBase):
    __tablename__ = "sms_message"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(Enum(SmsProvider))
    provider_message_id = Column(String)
