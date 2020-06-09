from pydantic import BaseModel

from .constants import Status


class MyModel(BaseModel):
    status: Status

    class Config:
        extra = 'forbid'

    @property
    def is_error(self) -> bool:
        return self.status == Status.ERROR
