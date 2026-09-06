from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


MilestoneStatus = Literal[
    "Planned",
    "In Progress",
    "Completed",
]


class MilestoneBase(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )
    status: MilestoneStatus = "Planned"
    due_date: date | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        cleaned_title = value.strip()

        if not cleaned_title:
            raise ValueError(
                "Milestone title must not be empty"
            )

        return cleaned_title


class MilestoneCreate(MilestoneBase):
    pass


class MilestoneUpdate(MilestoneBase):
    pass


class MilestonePatch(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    status: MilestoneStatus | None = None
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
                "Milestone title must not be empty"
            )

        return cleaned_title


class MilestoneResponse(MilestoneBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    progress: int = Field(
        ge=0,
        le=100,
    )

    model_config = ConfigDict(
        from_attributes=True,
    )