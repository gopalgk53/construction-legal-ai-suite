from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from database.dependency import get_db
from models.project import Project


router = APIRouter()


@router.get("/projects")
def get_projects(db: Session = Depends(get_db)):

    projects = db.query(Project).all()

    return projects