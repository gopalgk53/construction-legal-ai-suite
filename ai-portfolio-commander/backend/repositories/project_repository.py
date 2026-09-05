from sqlalchemy.orm import Session

from models.project import Project

def get_all_projects(
    db: Session,
    status: str | None = None,
    search: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    query = db.query(Project)

    if status is not None:
        query = query.filter(
            Project.status == status
        )

    if search is not None:
        query = query.filter(
            Project.name.ilike(f"%{search}%")
        )

    return (
        query
        .order_by(Project.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

def get_project_by_id(
    db: Session,
    project_id: int,
):
    return (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

def add_project(
    db: Session,
    project: Project,
):
    db.add(project)


def delete_project(
    db: Session,
    project: Project,
):
    db.delete(project)

def count_projects(
    db: Session,
    status: str | None = None,
    search: str | None = None,
) -> int:
    query = db.query(Project)

    if status is not None:
        query = query.filter(
            Project.status == status
        )

    if search is not None:
        query = query.filter(
            Project.name.ilike(f"%{search}%")
        )

    return query.count()