from pydantic import BaseModel


# register
class RegisterRequest(BaseModel):
    username: str


class RegisterResponse(BaseModel):
    status: str = 'OK'


# login
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    class _ClientNotFound(BaseModel):
        code: str = 'client_not_found'

    class _WrongPassword(BaseModel):
        code: str = 'wrong_password'

    refresh_token: str
    access_token: str


# check
class CheckTokenRequest(BaseModel):
    token: str


class CheckTokenResponse(BaseModel):
    class _InvalidToken(BaseModel):
        code: str = 'invalid_token'

    class _TokenExpired(BaseModel):
        code: str = 'token_expired'

    username: str
