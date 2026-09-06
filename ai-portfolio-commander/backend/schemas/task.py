from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


TaskStatus = Literal[
    "Planned",
    "In Progress",
    "Completed",
]

TaskPriority = Literal[
    "Low",
    "Medium",
    "High",
]


class TaskBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    title: str = Field(
        min_length=1,
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
    )
    status: TaskStatus = "Planned"
    priority: TaskPriority = "Medium"
    due_date: date | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        cleaned_title = value.strip()

        if not cleaned_title:
            raise ValueError(
                "Task title must not be empty"
            )

        return cleaned_title


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskPatch(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
    )
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None

    @field_validator("title")
    @classmethod
    def validate_title(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_title = value.strip()

        if not cleaned_title:
            raise ValueError(
                "Task title must not be empty"
            )

        return cleaned_title


class TaskResponse(TaskBase):
    id: int
    milestone_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )