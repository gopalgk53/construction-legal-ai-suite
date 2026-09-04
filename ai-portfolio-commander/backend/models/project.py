from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(255)
    )

    status: Mapped[str] = mapped_column(
        String(50)
    )

    progress: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    description: Mapped[str | None] = mapped_column(
    String(1000),
    nullable=True,
    )