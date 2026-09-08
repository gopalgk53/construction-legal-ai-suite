from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from database.dependency import get_db
from schemas.learning_session import (
    LearningSessionCreate,
    LearningSessionPatch,
    LearningSessionResponse,
    LearningSessionUpdate,
)
from services.learning_session_service import (
    create_learning_session,
    delete_learning_session,
    get_learning_session_by_id,
    get_learning_sessions,
    patch_learning_session,
    update_learning_session,
)


router = APIRouter(
    prefix="/learning-sessions",
    tags=["Learning Sessions"],
)


@router.post(
    "",
    response_model=LearningSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_learning_session_route(
    session_data: LearningSessionCreate,
    db: Session = Depends(get_db),
):
    return create_learning_session(
        db,
        session_data,
    )


@router.get(
    "",
    response_model=list[LearningSessionResponse],
)
def get_learning_sessions_route(
    db: Session = Depends(get_db),
):
    return get_learning_sessions(db)


@router.get(
    "/{learning_session_id}",
    response_model=LearningSessionResponse,
)
def get_learning_session_route(
    learning_session_id: int,
    db: Session = Depends(get_db),
):
    return get_learning_session_by_id(
        db,
        learning_session_id,
    )


@router.put(
    "/{learning_session_id}",
    response_model=LearningSessionResponse,
)
def update_learning_session_route(
    learning_session_id: int,
    session_data: LearningSessionUpdate,
    db: Session = Depends(get_db),
):
    return update_learning_session(
        db,
        learning_session_id,
        session_data,
    )


@router.patch(
    "/{learning_session_id}",
    response_model=LearningSessionResponse,
)
def patch_learning_session_route(
    learning_session_id: int,
    session_data: LearningSessionPatch,
    db: Session = Depends(get_db),
):
    return patch_learning_session(
        db,
        learning_session_id,
        session_data,
    )


@router.delete(
    "/{learning_session_id}",
)
def delete_learning_session_route(
    learning_session_id: int,
    db: Session = Depends(get_db),
):
    return delete_learning_session(
        db,
        learning_session_id,
    )