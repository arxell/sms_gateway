import logging

from fastapi import APIRouter

from app.domain.sms.service import SendSmsService

from .datamodels import SmsSendRequest, SmsSendResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/sms/send', response_model=SmsSendResponse)
async def send(request: SmsSendRequest) -> SmsSendResponse:
    logger.info(request)
    code = await SendSmsService.send(request.phone, request.text)
    return SmsSendResponse(code=code)
