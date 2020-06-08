from pydantic import BaseModel


class SmsSendRequest(BaseModel):
    phone: str
    text: str


class SmsSendResponse(BaseModel):
    code: str
