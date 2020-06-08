from fastapi import APIRouter

from .datamodels import CheckTokenResponse, LoginResponse, RegisterResponse
from .login import errors as login_errors
from .login import login
from .register import errors as register_errors
from .register import register
from .token import check_token
from .token import errors as check_token_errors

router = APIRouter()
router.add_api_route('/client/register', register, response_model=RegisterResponse, responses=register_errors)
router.add_api_route('/client/login', login, response_model=LoginResponse, responses=login_errors)
router.add_api_route('/token/check', check_token, response_model=CheckTokenResponse, responses=check_token_errors)
