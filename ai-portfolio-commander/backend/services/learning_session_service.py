from fastapi import HTTPException
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError,
)
from sqlalchemy.orm import Session

from models.learning_session import LearningSession
from repositories import learning_session_repository
from schemas.learning_session import (
    LearningSessionCreate,
    LearningSessionPatch,
    LearningSessionUpdate,
)


def create_learning_session(
    db: Session,
    session_data: LearningSessionCreate,
):
    existing_session = (
        learning_session_repository
        .get_learning_session_by_date(
            db,
            session_data.session_date,
        )
    )

    if existing_session is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "A learning session already exists "
                "for this date"
            ),
        )

    learning_session = LearningSession(
        session_date=session_data.session_date,
        status=session_data.status,
        planned_minutes=session_data.planned_minutes,
        completed_minutes=session_data.completed_minutes,
        focus=session_data.focus,
        learned=session_data.learned,
        challenges=session_data.challenges,
        improvements=session_data.improvements,
        tomorrow_priority=(
            session_data.tomorrow_priority
        ),
    )

    try:
        learning_session_repository.add_learning_session(
            db,
            learning_session,
        )
        db.commit()
        db.refresh(learning_session)

        return learning_session

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "A learning session already exists "
                "for this date"
            ),
        )

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to create learning session",
        )


def get_learning_sessions(
    db: Session,
):
    return (
        learning_session_repository
        .get_learning_sessions(db)
    )


def get_learning_session_by_id(
    db: Session,
    learning_session_id: int,
):
    learning_session = (
        learning_session_repository
        .get_learning_session_by_id(
            db,
            learning_session_id,
        )
    )

    if learning_session is None:
        raise HTTPException(
            status_code=404,
            detail="Learning session not found",
        )

    return learning_session


def update_learning_session(
    db: Session,
    learning_session_id: int,
    session_data: LearningSessionUpdate,
):
    learning_session = get_learning_session_by_id(
        db,
        learning_session_id,
    )

    existing_session = (
        learning_session_repository
        .get_learning_session_by_date(
            db,
            session_data.session_date,
        )
    )

    if (
        existing_session is not None
        and existing_session.id
        != learning_session_id
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "A learning session already exists "
                "for this date"
            ),
        )

    learning_session.session_date = (
        session_data.session_date
    )
    learning_session.status = session_data.status
    learning_session.planned_minutes = (
        session_data.planned_minutes
    )
    learning_session.completed_minutes = (
        session_data.completed_minutes
    )
    learning_session.focus = session_data.focus
    learning_session.learned = session_data.learned
    learning_session.challenges = (
        session_data.challenges
    )
    learning_session.improvements = (
        session_data.improvements
    )
    learning_session.tomorrow_priority = (
        session_data.tomorrow_priority
    )

    try:
        db.commit()
        db.refresh(learning_session)

        return learning_session

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "A learning session already exists "
                "for this date"
            ),
        )

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to update learning session",
        )


def patch_learning_session(
    db: Session,
    learning_session_id: int,
    session_data: LearningSessionPatch,
):
    learning_session = get_learning_session_by_id(
        db,
        learning_session_id,
    )

    update_data = session_data.model_dump(
        exclude_unset=True,
    )

    new_session_date = update_data.get(
        "session_date"
    )

    if (
        new_session_date is not None
        and new_session_date
        != learning_session.session_date
    ):
        existing_session = (
            learning_session_repository
            .get_learning_session_by_date(
                db,
                new_session_date,
            )
        )

        if existing_session is not None:
            raise HTTPException(
                status_code=409,
                detail=(
                    "A learning session already exists "
                    "for this date"
                ),
            )

    for field, value in update_data.items():
        setattr(
            learning_session,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(learning_session)

        return learning_session

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "A learning session already exists "
                "for this date"
            ),
        )

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to update learning session",
        )


def delete_learning_session(
    db: Session,
    learning_session_id: int,
):
    learning_session = get_learning_session_by_id(
        db,
        learning_session_id,
    )

    try:
        learning_session_repository.delete_learning_session(
            db,
            learning_session,
        )
        db.commit()

        return {
            "message": (
                "Learning session deleted successfully"
            )
        }

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to delete learning session",
        )