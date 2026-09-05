from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from datetime import datetime

class ProjectBase(BaseModel):
    name: str = Field(min_length=1)
    status: Literal["Planned", "In Progress", "Completed"]
    progress: int = Field(
        ge=0,
        le=100,
    )    
    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned_name = value.strip()

        if not cleaned_name:
            raise ValueError(
                "Project name must not be empty"
            )

        return cleaned_name


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class ProjectPatch(BaseModel):
    name: str | None = None
    status: Literal[
        "Planned",
        "In Progress",
        "Completed",
    ] | None = None
    progress: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
    )
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        cleaned_name = value.strip()

        if not cleaned_name:
            raise ValueError(
                "Project name must not be empty"
            )

        return cleaned_name

class ProjectResponse(BaseModel):
    id: int
    name: str
    status: str
    progress: int
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
    limit: int
    offset: int