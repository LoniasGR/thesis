from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
import sqlalchemy.sql.functions as func
from typing import List

from database import Base


class EvaluationDialoguesDB(Base):
    __tablename__ = "evaluation_user_dialogue_table"
    evaluation_id: Mapped[str] = mapped_column(
        ForeignKey("evaluations.uuid"), primary_key=True
    )
    user_dialogue_id: Mapped[int] = mapped_column(
        ForeignKey("user_dialogues.id"), primary_key=True
    )
    order: Mapped[int] = mapped_column(nullable=False)
    user_dialogue: Mapped[UserDialogueDB] = relationship()


class EvaluationDB(Base):
    __tablename__ = "evaluations"

    uuid: Mapped[str] = mapped_column(primary_key=True)
    suggestion: Mapped[str] = mapped_column(nullable=False)
    answer: Mapped[bool] = mapped_column(nullable=True)
    date_asked: Mapped[datetime] = mapped_column(default=func.now())
    date_answered: Mapped[datetime] = mapped_column(nullable=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    client: Mapped[ClientDB] = relationship(back_populates="evaluations")
    user_prompts: Mapped[List[EvaluationDialoguesDB]] = relationship()


class ClientDB(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    host: Mapped[str] = mapped_column(nullable=False)
    evaluations: Mapped[List[EvaluationDB]] = relationship(back_populates="client")

class UserDialogueDB(Base):
    __tablename__ = "user_dialogues"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    description: Mapped[str] = mapped_column(nullable=False)
    intent: Mapped[str] = mapped_column(nullable=False)
    response: Mapped[str] = mapped_column(nullable=False)
