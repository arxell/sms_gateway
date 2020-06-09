import logging
from http import HTTPStatus

from fastapi import APIRouter

from app.domain.auth.service import AuthService
from app.server.http.core import get_error

from .datamodels import CheckTokenRequest, CheckTokenResponse

router = APIRouter()
logger = logging.getLogger(__name__)
errors = {HTTPStatus.UNAUTHORIZED.value: {"model": CheckTokenResponse._InvalidToken}}


@router.post('/token/check', response_model=CheckTokenResponse, responses=errors)
async def check_token(request: CheckTokenRequest) -> CheckTokenResponse:
    logger.info(request)
    payload, error = AuthService.get_payload(request.token)
    if error:
        return get_error(errors, HTTPStatus.UNAUTHORIZED)
    return CheckTokenResponse(username=payload.username)
