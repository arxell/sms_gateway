from http import HTTPStatus
from typing import Dict

from fastapi.responses import JSONResponse
from pydantic import BaseModel


def get_error(error_responses: Dict[HTTPStatus, Dict[str, BaseModel]], status: HTTPStatus) -> JSONResponse:
    return JSONResponse(status_code=status, content=error_responses[status]['model']().dict())
