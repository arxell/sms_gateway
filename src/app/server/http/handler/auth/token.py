import logging
from http import HTTPStatus

from fastapi import APIRouter

from app.domain.auth.service import AuthService
from app.server.http.core import get_error

from .datamodels import CheckTokenRequest, CheckTokenResponse

router = APIRouter()
logger = logging.getLogger(__name__)
errors = {
    HTTPStatus.BAD_REQUEST.value: {"model": CheckTokenResponse._InvalidToken},
    HTTPStatus.UNAUTHORIZED.value: {"model": CheckTokenResponse._TokenExpired},
}


@router.post('/token/check', response_model=CheckTokenResponse, responses=errors)
async def check_token(request: CheckTokenRequest) -> CheckTokenResponse:
    logger.info(request)
    check_token_result = AuthService.check_token(request.token)
    if check_token_result.is_error:
        if check_token_result.is_error_expired:
            return get_error(errors, HTTPStatus.UNAUTHORIZED)
        else:
            return get_error(errors, HTTPStatus.BAD_REQUEST)

    return CheckTokenResponse(username=check_token_result.jwt_payload.username)
