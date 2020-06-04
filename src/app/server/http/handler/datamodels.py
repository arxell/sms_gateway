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
