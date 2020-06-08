from enum import Enum
from typing import List

from pydantic import BaseModel


class ReadyResponse(BaseModel):
    class _ServiceCheck(BaseModel):
        service: str
        is_ready: bool
        error: str

    is_ready: bool
    checks: List[_ServiceCheck]


class VersionResponse(BaseModel):
    build_date: str
    build_number: str
    git_branch_name: str
    git_short_hash: str
    version: str


class SmsSendRequest(BaseModel):
    phone: str
    text: str


class SmsSendResponse(BaseModel):
    code: str


# login
class LoginRequest(BaseModel):
    client_id: str
    password: str


class LoginResponse(BaseModel):
    class _ClientNotFound(BaseModel):
        code: str = 'client_not_found'

    class _WrongPassword(BaseModel):
        code: str = 'wrong_password'

    token: str


# check
class CheckTokenRequest(BaseModel):
    token: str


class CheckTokenResponse(BaseModel):
    class _InvalidToken(BaseModel):
        code: str = 'invalid_token'

    status: str = 'OK'
