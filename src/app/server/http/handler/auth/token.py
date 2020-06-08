import logging
from http import HTTPStatus

import jwt

from app.conf.sentry import settings
from app.server.http.core import get_error

from .datamodels import CheckTokenRequest, CheckTokenResponse

logger = logging.getLogger(__name__)
errors = {HTTPStatus.UNAUTHORIZED: {"model": CheckTokenResponse._InvalidToken}}


async def check_token(request: CheckTokenRequest) -> CheckTokenResponse:
    logger.info(request)
    try:
        jwt.decode(request.token, settings.jwt_sectet, algorithms=['HS256'])
    except Exception:
        logger.exception('jwt unknown error')
        return get_error(errors, HTTPStatus.UNAUTHORIZED)
    return CheckTokenResponse(status='OK')
