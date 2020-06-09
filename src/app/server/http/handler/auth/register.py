import logging
from http import HTTPStatus

from fastapi import APIRouter

from app.domain.auth.service import AuthService
from app.server.http.core import get_error

from .datamodels import RegisterRequest, RegisterResponse

router = APIRouter()
logger = logging.getLogger(__name__)
errors = {HTTPStatus.INTERNAL_SERVER_ERROR: {"model": RegisterResponse._Unknown}}


@router.post('/client/register', response_model=RegisterResponse, responses=errors)
async def register(request: RegisterRequest) -> RegisterResponse:
    logger.info(request)

    login_result = await AuthService.login(request.phone)
    if login_result.is_error:
        return get_error(errors, HTTPStatus.INTERNAL_SERVER_ERROR)
    else:
        return RegisterResponse()
