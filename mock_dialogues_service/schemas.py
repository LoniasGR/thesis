from typing import Optional
from pydantic import BaseModel


class Client(BaseModel):
    id: int
    host: str

    class Config:
        from_attributes = True


class UserUtterance(BaseModel):
    intent: str
    description: str

    class Config:
        from_attributes = True


class Evaluation(BaseModel):
    uuid: str | None
    user: list[str] | list[UserUtterance]
    suggestion: str
    answer: bool | None
    client: Client | None

    class Config:
        from_attributes = True
