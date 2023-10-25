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


class EvaluationBase(BaseModel):
    uuid: str | None
    answer: bool | None

    class Config:
        from_attributes = True


class Evaluation(EvaluationBase):
    user: list[str] | list[UserUtterance]
    suggestion: str
    client: Client | None
