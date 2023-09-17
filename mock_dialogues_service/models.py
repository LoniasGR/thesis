from pydantic import BaseModel


class Evaluation(BaseModel):
    user: list[str]
    suggestion: str
    answer: bool
