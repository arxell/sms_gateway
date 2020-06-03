import logging

from fastapi import APIRouter

from app.sms.client import sms_client

from .datamodels import SmsSendRequest, SmsSendResponse

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post('/sms/send', response_model=SmsSendResponse)
async def send(request: SmsSendRequest) -> SmsSendResponse:
    logger.info(request)
    code = await sms_client.send(request.phone, request.text)
    return SmsSendResponse(code=code)
