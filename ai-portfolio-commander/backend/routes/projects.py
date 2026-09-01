from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.dependency import get_db
from schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from services.project_service import (
    create_project,
    delete_project,
    get_project_by_id,
    get_projects,
    update_project,
)



router = APIRouter()


@router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
)
def get_project_route(
    project_id: int,
    db: Session = Depends(get_db),
):
    return get_project_by_id(
        db,
        project_id,
    )

@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)

def create_project_route(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
):
    return create_project(
        db,
        project_data,
    )


@router.delete("/projects/{project_id}")
def delete_project_route(
    project_id: int,
    db: Session = Depends(get_db),
):
    return delete_project(
        db,
        project_id,
    )


@router.get(
    "/projects",
    response_model=list[ProjectResponse],
)
def get_projects_route(
    db: Session = Depends(get_db),
):
    return get_projects(db)


@router.put(
    "/projects/{project_id}",
    response_model=ProjectResponse,
)
def update_project_route(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
):
    return update_project(
        db,
        project_id,
        project_data,
    )