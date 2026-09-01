from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1)
    status: Literal["Planned", "In Progress", "Completed"]
    progress: int = Field(ge=0, le=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned_name = value.strip()

        if not cleaned_name:
            raise ValueError("Project name must not be empty")

        return cleaned_name


class ProjectUpdate(BaseModel):
    name: str = Field(min_length=1)
    status: Literal["Planned", "In Progress", "Completed"]
    progress: int = Field(
        ge=0,
        le=100,
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


class ProjectResponse(BaseModel):
    id: int
    name: str
    status: str
    progress: int

    model_config = ConfigDict(from_attributes=True)