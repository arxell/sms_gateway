import logging

import jwt
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.conf.sentry import settings

from .datamodels import CheckTokenRequest, CheckTokenResponse

router = APIRouter()
logger = logging.getLogger(__name__)
error_responses = {401: {"model": CheckTokenResponse._InvalidToken}}


@router.post('/token/check', response_model=CheckTokenResponse, responses=error_responses)
async def check_token(request: CheckTokenRequest) -> CheckTokenResponse:
    logger.info(request)
    try:
        jwt.decode(request.token, settings.jwt_sectet, algorithms=['HS256'])
    except Exception:
        logger.exception('jwt unknown error')
        return JSONResponse(status_code=401, content=error_responses[401]['model']().dict())
    return CheckTokenResponse(status='OK')
