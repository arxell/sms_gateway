import logging

import jwt
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .datamodels import CheckTokenRequest, CheckTokenResponse, LoginRequest, LoginResponse

logger = logging.getLogger(__name__)

router = APIRouter()

secret = 'secret'


login_error_responses = {401: {"model": LoginResponse._WrongPassword}, 404: {"model": LoginResponse._ClientNotFound}}


@router.post('/api/auth/login', response_model=LoginResponse, responses=login_error_responses)
async def login(request: LoginRequest) -> LoginResponse:
    logger.info(request)

    if False:
        # check client_id in db
        return JSONResponse(status_code=404, content=login_error_responses[404]['model']().dict())

    if False:
        # check log/pass in db
        return JSONResponse(status_code=401, content=login_error_responses[401]['model']().dict())

    token = jwt.encode({'client_id': request.client_id}, secret, algorithm='HS256')
    return LoginResponse(token=token)


check_token_error_responses = {401: {"model": CheckTokenResponse._InvalidToken}}


@router.post('/api/auth/check', response_model=CheckTokenResponse, responses=check_token_error_responses)
async def check_token(request: CheckTokenRequest) -> CheckTokenResponse:
    logger.info(request)
    try:
        jwt.decode(request.token, secret, algorithms=['HS256'])
    except Exception:
        logger.exception('jwt unknown error')
        return JSONResponse(status_code=401, content=check_token_error_responses[401]['model']().dict())
    return CheckTokenResponse(status='OK')
