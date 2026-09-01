from sqlalchemy.orm import Session

from models.project import Project

def get_all_projects(
    db: Session,
):
    return db.query(Project).all()

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