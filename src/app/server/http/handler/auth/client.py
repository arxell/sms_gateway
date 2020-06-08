import logging

import jwt
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .datamodels import LoginRequest, LoginResponse

router = APIRouter()

logger = logging.getLogger(__name__)
secret = 'secret'
error_responses = {401: {"model": LoginResponse._WrongPassword}, 404: {"model": LoginResponse._ClientNotFound}}


@router.post('/client/login', response_model=LoginResponse, responses=error_responses)
async def login(request: LoginRequest) -> LoginResponse:
    logger.info(request)

    if False:
        # check client_id in db
        return JSONResponse(status_code=404, content=error_responses[404]['model']().dict())

    if False:
        # check log/pass in db
        return JSONResponse(status_code=401, content=error_responses[401]['model']().dict())

    token = jwt.encode({'client_id': request.client_id}, secret, algorithm='HS256')
    return LoginResponse(token=token)


@router.post('/client/logout')
async def logout():
    pass
