from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import JSON, CheckConstraint, Column, Field, SQLModel, UniqueConstraint


class SampledDialogue(SQLModel, table=True):
    uuid: str = Field(primary_key=True)
    dialogue: str = Field(nullable=False)
    goal: str = Field()
    smart_suggestion: str = Field(nullable=True)
    random_suggestion: str = Field(nullable=True)
    popularity_suggestion: str = Field(nullable=True)
    llm_suggestion: str = Field(nullable=True)
    source_choice: str = Field(nullable=True)
    source_choice_reason: str = Field(nullable=True)


class AnonymousEvaluator(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    public_token: UUID = Field(default_factory=uuid4, unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Evaluation(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("presentation_id", name="uq_evaluation_presentation"),
        CheckConstraint(
            "relevance_score IS NULL OR relevance_score BETWEEN 1 AND 5",
            name="ck_evaluation_relevance_score",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    presentation_id: UUID = Field(
        foreign_key="evaluationpresentation.id",
        nullable=False,
        ondelete="CASCADE",
        index=True,
    )
    choice: str = Field(nullable=False)
    choice_reason: str = Field(nullable=True)
    relevance_score: int = Field(nullable=True)
    no_good_option: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=False
    )


class EvaluationPresentation(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "evaluator_id", "dialogue_id", name="uq_presentation_evaluator_dialogue"
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    evaluator_id: UUID = Field(
        foreign_key="anonymousevaluator.id",
        nullable=False,
        ondelete="CASCADE",
        index=True,
    )
    dialogue_id: str = Field(
        foreign_key="sampleddialogue.uuid",
        nullable=False,
        ondelete="CASCADE",
        index=True,
    )
    display_order: list[str] = Field(sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=False
    )
