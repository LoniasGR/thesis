from __future__ import annotations

from typing import List
from datetime import datetime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import sqlalchemy.sql.functions as func

from models.schemas import ResponseSelection


class Base(DeclarativeBase):
    pass


class ComparisonDialoguesDB(Base):
    __tablename__ = "comparison_user_dialogue_table"

    comparison_id: Mapped[str] = mapped_column(
        ForeignKey("comparisons.uuid"), primary_key=True
    )
    user_dialogue_id: Mapped[str] = mapped_column(
        ForeignKey("user_dialogues.intent"), primary_key=True
    )
    order: Mapped[int] = mapped_column(nullable=False)
    user_dialogue: Mapped[UserDialogueDB] = relationship()


class ComparisonsDB(Base):
    __tablename__ = "comparisons"

    uuid: Mapped[str] = mapped_column(primary_key=True)
    response: Mapped[ResponseSelection] = mapped_column(nullable=True)
    date_asked: Mapped[datetime] = mapped_column(default=func.now())
    date_answered: Mapped[datetime] = mapped_column(nullable=True)
    random_intent: Mapped[str] = mapped_column(nullable=False)
    smart_intent: Mapped[str] = mapped_column(nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    client: Mapped[ClientDB] = relationship(back_populates="evaluations")
    user_prompts: Mapped[List[ComparisonDialoguesDB]] = relationship()


class ClientDB(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    host: Mapped[str] = mapped_column(nullable=False)
    evaluations: Mapped[List[ComparisonsDB]] = relationship(back_populates="client")


class UserDialogueDB(Base):
    __tablename__ = "user_dialogues"

    description: Mapped[str] = mapped_column(nullable=False)
    intent: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    response: Mapped[str] = mapped_column(nullable=False)
