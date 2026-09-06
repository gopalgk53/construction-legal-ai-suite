from sqlalchemy.orm import Session

from models.task import Task


def get_tasks_by_milestone(
    db: Session,
    milestone_id: int,
):
    return (
        db.query(Task)
        .filter(Task.milestone_id == milestone_id)
        .order_by(Task.id)
        .all()
    )


def get_task_by_id(
    db: Session,
    milestone_id: int,
    task_id: int,
):
    return (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.milestone_id == milestone_id,
        )
        .first()
    )


def add_task(
    db: Session,
    task: Task,
):
    db.add(task)


def delete_task(
    db: Session,
    task: Task,
):
    db.delete(task)