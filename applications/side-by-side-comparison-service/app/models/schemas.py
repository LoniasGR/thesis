from pydantic import BaseModel
from enum import Enum


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


class UserUtterance(BaseModel):
    intent: str
    description: str
    response: str

    class Config:
        from_attributes = True


class Client(BaseModel):
    id: int
    host: str

    class Config:
        from_attributes = True


class ResponseSelection(Enum):
    RANDOM = 1
    SMART = 2


class ComparisonBase(BaseModel):
    uuid: str | None
    response: ResponseSelection | None

    class Config:
        from_attributes = True


class ComparisonSuggestion(ComparisonBase):
    user: list[UserUtterance]
    random_intent: str
    random_utterance: str
    smart_intent: str
    smart_utterance: str
