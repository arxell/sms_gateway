import logging
from http import HTTPStatus

import jwt

from app.conf.sentry import settings
from app.server.http.core import get_error

from .datamodels import LoginRequest, LoginResponse

logger = logging.getLogger(__name__)
errors = {
    HTTPStatus.UNAUTHORIZED.value: {"model": LoginResponse._WrongPassword},
    HTTPStatus.NOT_FOUND.value: {"model": LoginResponse._ClientNotFound},
    HTTPStatus.INTERNAL_SERVER_ERROR.value: {"model": LoginResponse._Unknown},
}


async def login(request: LoginRequest) -> LoginResponse:
    logger.info(request)

    if False:
        # check client_id in db
        return get_error(errors, HTTPStatus.NOT_FOUND)

    if False:
        # check log/pass in db
        return get_error(errors, HTTPStatus.UNAUTHORIZED)

    try:
        token = jwt.encode({'client_id': request.client_id}, settings.jwt_sectet, algorithm='HS256')
    except Exception:
        logger.exception('jwt unknown error')
        return get_error(errors, HTTPStatus.INTERNAL_SERVER_ERROR)

    return LoginResponse(token=token)


async def logout():
    pass
