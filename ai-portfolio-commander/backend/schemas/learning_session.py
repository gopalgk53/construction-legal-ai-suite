from datetime import date, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


LearningSessionStatus = Literal[
    "Planned",
    "In Progress",
    "Completed",
]


class LearningSessionBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    session_date: date
    status: LearningSessionStatus = "Planned"
    planned_minutes: int = Field(
        ge=1,
        le=1440,
    )
    completed_minutes: int = Field(
        default=0,
        ge=0,
        le=1440,
    )
    focus: str = Field(
        min_length=1,
        max_length=500,
    )
    learned: str | None = None
    challenges: str | None = None
    improvements: str | None = None
    tomorrow_priority: str | None = None

    @field_validator("focus")
    @classmethod
    def validate_focus(cls, value: str) -> str:
        cleaned_focus = value.strip()

        if not cleaned_focus:
            raise ValueError(
                "Session focus must not be empty"
            )

        return cleaned_focus


class LearningSessionCreate(LearningSessionBase):
    pass


class LearningSessionUpdate(LearningSessionBase):
    pass


class LearningSessionPatch(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    session_date: date | None = None
    status: LearningSessionStatus | None = None
    planned_minutes: int | None = Field(
        default=None,
        ge=1,
        le=1440,
    )
    completed_minutes: int | None = Field(
        default=None,
        ge=0,
        le=1440,
    )
    focus: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )
    learned: str | None = None
    challenges: str | None = None
    improvements: str | None = None
    tomorrow_priority: str | None = None

    @field_validator(
        "session_date",
        "status",
        "planned_minutes",
        "completed_minutes",
    )
    @classmethod
    def reject_null_required_fields(
        cls,
        value,
    ):
        if value is None:
            raise ValueError(
                "Required session fields cannot be null"
            )

        return value

    @field_validator("focus")
    @classmethod
    def validate_focus(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            raise ValueError(
                "Session focus cannot be null"
            )

        cleaned_focus = value.strip()

        if not cleaned_focus:
            raise ValueError(
                "Session focus must not be empty"
            )

        return cleaned_focus


class LearningSessionResponse(LearningSessionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )