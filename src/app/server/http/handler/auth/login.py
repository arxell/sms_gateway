import logging
from http import HTTPStatus

from fastapi import APIRouter

from app.datamodels import Unknown
from app.domain.auth.service import AuthService
from app.server.http.core import get_error

from .datamodels import LoginRequest, LoginResponse

logger = logging.getLogger(__name__)
router = APIRouter()
errors = {
    HTTPStatus.UNAUTHORIZED.value: {"model": LoginResponse._WrongPassword},
    HTTPStatus.NOT_ACCEPTABLE.value: {"model": LoginResponse._CodeWasUsed},
    HTTPStatus.NOT_FOUND.value: {"model": LoginResponse._ClientNotFound},
    HTTPStatus.INTERNAL_SERVER_ERROR.value: {"model": Unknown},
}


@router.post('/client/login', response_model=LoginResponse, responses=errors)
async def login(request: LoginRequest) -> LoginResponse:
    logger.info(request)

    check_code_result = await AuthService.check_code(request.username, request.password)
    if check_code_result.is_error:
        if check_code_result.error == check_code_result._Error.CLIENT_NOT_FOUND:
            return get_error(errors, HTTPStatus.NOT_FOUND)
        elif check_code_result.error == check_code_result._Error.CODE_WAS_USED:
            return get_error(errors, HTTPStatus.NOT_ACCEPTABLE)
        elif check_code_result.error == check_code_result._Error.INVALID_CODE:
            return get_error(errors, HTTPStatus.UNAUTHORIZED)
        else:
            return get_error(errors, HTTPStatus.INTERNAL_SERVER_ERROR)
    else:
        return LoginResponse(
            refresh_token=check_code_result.data.refresh_token, access_token=check_code_result.data.access_token
        )
