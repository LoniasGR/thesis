from logging import Logger
from pydantic import BaseModel
from datetime import datetime

class SuggestionRequestData(BaseModel):
    uid: str
    previous_intents: list[str]
    previous_suggestions: list[str]
    remaining_suggestions: list[str]
    intent: str

    def log(self, logger: Logger) -> None:
        logger.debug("{")
        for k, v in self:
            logger.debug(f"     {k}: {v}")
        logger.debug("}")


class UserIntentRequestData(BaseModel):
    uid: str
    intent: str

    def log(self, logger: Logger) -> None:
        logger.debug("{")
        for k, v in self:
            logger.debug(f"     {k}: {v}")
        logger.debug("}")


class BaseResponse(BaseModel):
    error: str | None


class Suggestion(BaseResponse):
    action: int | None


class UserData(BaseModel):
    uid: str
    intent: str
    previous_intents: list[str]
    previous_suggestions: list[str]
    remaining_suggestions: list[str]
    recommendation: str
    recommendation_probability: float
    recommendation_cost: float
    awaits_results: bool
    awaits_intent: bool
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        orm_mode = True

    def set_historic_data(self, data: SuggestionRequestData) -> None:
        self.previous_intents = data.previous_intents
        self.previous_suggestions = data.previous_suggestions
        self.remaining_suggestions = data.remaining_suggestions
        self.intent = data.intent

    def set_recommendation_data(
        self, recommendation: str, recommendation_prob: float
    ) -> None:
        self.recommendation = recommendation
        self.recommendation_probability = recommendation_prob

    def set_cost(self, cost: float) -> None:
        self.recommendation_cost = cost

    def log(self, logger: Logger) -> None:
        logger.debug("{")
        for k, v in self:
            logger.debug(f"     {k}: {v}")
        logger.debug("}")
