from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DialogueDB(Base):
    __tablename__ = "dialogues"

    uuid: Mapped[str] = mapped_column(primary_key=True)
    dialogue: Mapped[str] = mapped_column(nullable=False)
    goal: Mapped[str] = mapped_column()
    smart_suggestion: Mapped[str] = mapped_column(nullable=True)
    random_suggestion: Mapped[str] = mapped_column(nullable=True)
    popularity_suggestion: Mapped[str] = mapped_column(nullable=True)
    llm_suggestion: Mapped[str] = mapped_column(nullable=True)
    choice: Mapped[str] = mapped_column(nullable=True)
    choice_reason: Mapped[str] = mapped_column(nullable=True)
