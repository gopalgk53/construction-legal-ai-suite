from pydantic import BaseModel


class ProjectResponse(BaseModel):
    id: int
    name: str
    status: str
    progress: int

    class Config:
        from_attributes = True