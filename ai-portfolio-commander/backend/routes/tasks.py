from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.dependency import get_db
from schemas.task import (
    TaskCreate,
    TaskPatch,
    TaskResponse,
    TaskUpdate,
)
from services.task_service import (
    create_task,
    delete_task,
    get_task_by_id,
    get_tasks,
    patch_task,
    update_task,
)


router = APIRouter(
    prefix=(
        "/projects/{project_id}"
        "/milestones/{milestone_id}"
        "/tasks"
    ),
    tags=["Tasks"],
)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task_route(
    project_id: int,
    milestone_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
):
    return create_task(
        db,
        project_id,
        milestone_id,
        task_data,
    )


@router.get(
    "",
    response_model=list[TaskResponse],
)
def get_tasks_route(
    project_id: int,
    milestone_id: int,
    db: Session = Depends(get_db),
):
    return get_tasks(
        db,
        project_id,
        milestone_id,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task_route(
    project_id: int,
    milestone_id: int,
    task_id: int,
    db: Session = Depends(get_db),
):
    return get_task_by_id(
        db,
        project_id,
        milestone_id,
        task_id,
    )


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
)
def update_task_route(
    project_id: int,
    milestone_id: int,
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
):
    return update_task(
        db,
        project_id,
        milestone_id,
        task_id,
        task_data,
    )


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
def patch_task_route(
    project_id: int,
    milestone_id: int,
    task_id: int,
    task_data: TaskPatch,
    db: Session = Depends(get_db),
):
    return patch_task(
        db,
        project_id,
        milestone_id,
        task_id,
        task_data,
    )


@router.delete("/{task_id}")
def delete_task_route(
    project_id: int,
    milestone_id: int,
    task_id: int,
    db: Session = Depends(get_db),
):
    return delete_task(
        db,
        project_id,
        milestone_id,
        task_id,
    )