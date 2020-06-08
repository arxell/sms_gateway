import logging
from http import HTTPStatus

from app.server.http.core import get_error

from .datamodels import RegisterRequest, RegisterResponse

logger = logging.getLogger(__name__)
errors = {HTTPStatus.CONFLICT: {"model": RegisterResponse._AlreadyExists}}


async def register(request: RegisterRequest) -> RegisterResponse:
    logger.info(request)

    if False:
        return get_error(errors)

    return RegisterResponse()
