from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from database.dependency import get_db
from models.project import Project

from schemas.project import ProjectResponse


router = APIRouter()


@router.get(
    "/projects",
    response_model=list[ProjectResponse]
)
def get_projects(
    db: Session = Depends(get_db)
):
    return db.query(Project).all()