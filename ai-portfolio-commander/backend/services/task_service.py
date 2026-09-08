from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.milestone import Milestone
from models.project import Project
from models.task import Task
from repositories import task_repository
from schemas.task import (
    TaskCreate,
    TaskPatch,
    TaskUpdate,
)
from services.milestone_service import (
    get_milestone_by_id as get_scoped_milestone,
)

def create_task(
    db: Session,
    project_id: int,
    milestone_id: int,
    task_data: TaskCreate,
):
    milestone = get_scoped_milestone(
        db,
        project_id,
        milestone_id,
    )

    task = Task(
        milestone_id=milestone_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
    )

    try:
        task_repository.add_task(
            db,
            task,
        )
        db.flush()

        recalculate_milestone_progress(
            db,
            milestone,
        )

        recalculate_project_progress(
            db,
            milestone.project,
        )

        db.commit()
        db.refresh(task)

        return task

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to create task",
        )


def get_tasks(
    db: Session,
    project_id: int,
    milestone_id: int,
):
    get_scoped_milestone(
        db,
        project_id,
        milestone_id,
    )

    return task_repository.get_tasks_by_milestone(
        db,
        milestone_id,
    )


def get_task_by_id(
    db: Session,
    project_id: int,
    milestone_id: int,
    task_id: int,
):
    get_scoped_milestone(
        db,
        project_id,
        milestone_id,
    )

    task = task_repository.get_task_by_id(
        db,
        milestone_id,
        task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


def update_task(
    db: Session,
    project_id: int,
    milestone_id: int,
    task_id: int,
    task_data: TaskUpdate,
):
    task = get_task_by_id(
        db,
        project_id,
        milestone_id,
        task_id,
    )

    task.title = task_data.title
    task.description = task_data.description
    task.status = task_data.status
    task.priority = task_data.priority
    task.due_date = task_data.due_date

    try:
        db.flush()

        recalculate_milestone_progress(
            db,
            task.milestone,
        )

        recalculate_project_progress(
            db,
            task.milestone.project,
        )

        db.commit()
        db.refresh(task)

        return task

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to update task",
        )


def patch_task(
    db: Session,
    project_id: int,
    milestone_id: int,
    task_id: int,
    task_data: TaskPatch,
):
    task = get_task_by_id(
        db,
        project_id,
        milestone_id,
        task_id,
    )

    update_data = task_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(task, field, value)

    try:
        db.flush()

        recalculate_milestone_progress(
            db,
            task.milestone,
        )
        recalculate_project_progress(
            db,
            task.milestone.project,
        )
        db.commit()
        db.refresh(task)

        return task

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to update task",
        )


def delete_task(
    db: Session,
    project_id: int,
    milestone_id: int,
    task_id: int,
):
    task = get_task_by_id(
        db,
        project_id,
        milestone_id,
        task_id,
    )

    milestone = task.milestone

    try:
        task_repository.delete_task(
            db,
            task,
        )
        db.flush()

        recalculate_milestone_progress(
            db,
            milestone,
        )

        recalculate_project_progress(
            db,
            milestone.project,
        )

        db.commit()
        return {
            "message": "Task deleted successfully"
        }
    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to delete task",
        )

def recalculate_milestone_progress(
    db: Session,
    milestone: Milestone,
) -> None:
    total, completed = (
        task_repository.get_task_completion_counts(
            db,
            milestone.id,
        )
    )

    if total == 0:
        progress = 0
    else:
        progress = round(
            completed * 100 / total
        )

    milestone.progress = progress

    if completed == 0:
        milestone.status = "Planned"
    elif completed == total:
        milestone.status = "Completed"
    else:
        milestone.status = "In Progress"


def recalculate_project_progress(
    db: Session,
    project: Project,
) -> None:
    total, completed = (
        task_repository.get_project_task_completion_counts(
            db,
            project.id,
        )
    )

    if total == 0:
        progress = 0
    else:
        progress = round(
            completed * 100 / total
        )

    project.progress = progress

    if completed == 0:
        project.status = "Planned"
    elif completed == total:
        project.status = "Completed"
    else:
        project.status = "In Progress"
