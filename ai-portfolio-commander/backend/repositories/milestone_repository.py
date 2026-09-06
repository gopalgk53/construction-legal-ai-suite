from sqlalchemy.orm import Session

from models.milestone import Milestone


def get_milestones_by_project(
    db: Session,
    project_id: int,
):
    return (
        db.query(Milestone)
        .filter(Milestone.project_id == project_id)
        .order_by(Milestone.id)
        .all()
    )


def get_milestone_by_id(
    db: Session,
    project_id: int,
    milestone_id: int,
):
    return (
        db.query(Milestone)
        .filter(
            Milestone.id == milestone_id,
            Milestone.project_id == project_id,
        )
        .first()
    )


def add_milestone(
    db: Session,
    milestone: Milestone,
):
    db.add(milestone)


def delete_milestone(
    db: Session,
    milestone: Milestone,
):
    db.delete(milestone)