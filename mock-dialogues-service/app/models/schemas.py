from pydantic import BaseModel


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


class Client(BaseModel):
    id: int
    host: str

    class Config:
        from_attributes = True


class UserUtterance(BaseModel):
    intent: str
    description: str
    response: str

    class Config:
        from_attributes = True


class EvaluationBase(BaseModel):
    uuid: str | None
    answer: bool | None

    class Config:
        from_attributes = True


class Suggestion(EvaluationBase):
    user: list[str] | list[UserUtterance]
    suggestion: str
    suggestion_utterance: str


class Evaluation(EvaluationBase):
    user: list[str] | list[UserUtterance]
    suggestion: str
    client: Client | None
