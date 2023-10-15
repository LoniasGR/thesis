from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from typing import List

from database import Base


evaluation_user_dialogue_table = Table(
    "evaluation_user_dialogue_table",
    Base.metadata,
    Column("evaluation_id", ForeignKey("evaluations.id"), primary_key=True),
    Column("user_dialogue_id", ForeignKey("user_dialogues.id"), primary_key=True),
    Column("order", Integer),
)

class EvaluationDB(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    suggestion: Mapped[str] = mapped_column(nullable=False)
    answer: Mapped[bool] = mapped_column(nullable=False)
    client: Mapped["ClientDB"] = relationship(back_populates="evaluations")
    user_prompts: Mapped[List["UserDialogueDB"]] = relationship(secondary=evaluation_user_dialogue_table)
class ClientDB(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    host: Mapped[str] = mapped_column(nullable=False)
    evaluations: Mapped[List["EvaluationDB"]] = relationship(back_populates="client")

class UserDialogueDB(Base):
    __tablename__ = "user_dialogues"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    description: Mapped[str] = mapped_column(nullable=False)
    intent: Mapped[str] = mapped_column(nullable=False)
