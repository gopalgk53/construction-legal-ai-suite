from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.milestone import Milestone
from repositories import (
    milestone_repository,
    project_repository,
)
from schemas.milestone import (
    MilestoneCreate,
    MilestonePatch,
    MilestoneUpdate,
)


def ensure_project_exists(
    db: Session,
    project_id: int,
) -> None:
    project = project_repository.get_project_by_id(
        db,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )


def create_milestone(
    db: Session,
    project_id: int,
    milestone_data: MilestoneCreate,
):
    ensure_project_exists(db, project_id)

    milestone = Milestone(
        project_id=project_id,
        title=milestone_data.title,
        status=milestone_data.status,
        due_date=milestone_data.due_date,
    )

    try:
        milestone_repository.add_milestone(
            db,
            milestone,
        )
        db.commit()
        db.refresh(milestone)

        return milestone

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to create milestone",
        )


def get_milestones(
    db: Session,
    project_id: int,
):
    ensure_project_exists(db, project_id)

    return milestone_repository.get_milestones_by_project(
        db,
        project_id,
    )


def get_milestone_by_id(
    db: Session,
    project_id: int,
    milestone_id: int,
):
    ensure_project_exists(db, project_id)

    milestone = milestone_repository.get_milestone_by_id(
        db,
        project_id,
        milestone_id,
    )

    if milestone is None:
        raise HTTPException(
            status_code=404,
            detail="Milestone not found",
        )

    return milestone

def update_milestone(
    db: Session,
    project_id: int,
    milestone_id: int,
    milestone_data: MilestoneUpdate,
):
    milestone = get_milestone_by_id(
        db,
        project_id,
        milestone_id,
    )

    milestone.title = milestone_data.title
    milestone.status = milestone_data.status
    milestone.due_date = milestone_data.due_date

    try:
        db.commit()
        db.refresh(milestone)

        return milestone

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to update milestone",
        )


def patch_milestone(
    db: Session,
    project_id: int,
    milestone_id: int,
    milestone_data: MilestonePatch,
):
    milestone = get_milestone_by_id(
        db,
        project_id,
        milestone_id,
    )

    update_data = milestone_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(milestone, field, value)

    try:
        db.commit()
        db.refresh(milestone)

        return milestone

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to update milestone",
        )


def delete_milestone(
    db: Session,
    project_id: int,
    milestone_id: int,
):
    milestone = get_milestone_by_id(
        db,
        project_id,
        milestone_id,
    )

    try:
        milestone_repository.delete_milestone(
            db,
            milestone,
        )
        db.commit()

        return {
            "message": "Milestone deleted successfully"
        }

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to delete milestone",
        )