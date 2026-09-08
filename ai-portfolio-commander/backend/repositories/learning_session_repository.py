from datetime import date

from sqlalchemy.orm import Session

from models.learning_session import LearningSession


def add_learning_session(
    db: Session,
    learning_session: LearningSession,
) -> None:
    db.add(learning_session)


def get_learning_sessions(
    db: Session,
):
    return (
        db.query(LearningSession)
        .order_by(
            LearningSession.session_date.desc(),
        )
        .all()
    )


def get_learning_session_by_id(
    db: Session,
    learning_session_id: int,
):
    return (
        db.query(LearningSession)
        .filter(
            LearningSession.id
            == learning_session_id,
        )
        .first()
    )


def get_learning_session_by_date(
    db: Session,
    session_date: date,
):
    return (
        db.query(LearningSession)
        .filter(
            LearningSession.session_date
            == session_date,
        )
        .first()
    )


def delete_learning_session(
    db: Session,
    learning_session: LearningSession,
) -> None:
    db.delete(learning_session)