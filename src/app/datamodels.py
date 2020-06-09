from pydantic import BaseModel

from .constants import Status


class Unknown(BaseModel):
    code: str = 'unknown'


class MyResultModel(BaseModel):
    status: Status

    class Config:
        extra = 'forbid'

    @property
    def is_error(self) -> bool:
        return self.status == Status.ERROR
