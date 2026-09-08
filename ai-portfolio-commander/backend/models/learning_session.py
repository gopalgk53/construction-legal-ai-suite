from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    session_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        unique=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="Planned",
        server_default="Planned",
        nullable=False,
    )

    planned_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    completed_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    focus: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    learned: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    challenges: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    improvements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    tomorrow_priority: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )