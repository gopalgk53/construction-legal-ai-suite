from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.project import Project
from schemas.project import ProjectCreate
from schemas.project import ProjectUpdate
from repositories import project_repository


def create_project(
    db: Session,
    project_data: ProjectCreate,
):
    db_project = Project(
        name=project_data.name,
        status=project_data.status,
        progress=project_data.progress,
    )

    try:
        project_repository.add_project(db, db_project)
        db.commit()
        db.refresh(db_project)

        return db_project

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to create project",
        )


def get_projects(
    db: Session,
):
    return project_repository.get_all_projects(db)

def get_project_by_id(
    db: Session,
    project_id: int,
):
    project = project_repository.get_project_by_id(
        db,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project

def update_project(
    db: Session,
    project_id: int,
    project_data: ProjectUpdate,
):
    project = project_repository.get_project_by_id(
        db,
        project_id,
        )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    project.name = project_data.name
    project.status = project_data.status
    project.progress = project_data.progress

    try:
        db.commit()
        db.refresh(project)

        return project

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to update project",
        )

def delete_project(
    db: Session,
    project_id: int,
):
    project = project_repository.get_project_by_id(
        db,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    try:
        project_repository.delete_project(db, project)
        db.commit()

        return {
            "message": "Project deleted successfully"
        }

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to delete project",
        )