import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings
from database.base import Base
from database.dependency import get_db
from main import app
from models.project import Project


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


if settings.test_database_url is None:
    raise RuntimeError(
        "TEST_DATABASE_URL must be configured for integration tests"
    )

TEST_DATABASE_URL = settings.test_database_url


test_engine = create_engine(
    TEST_DATABASE_URL
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=test_engine)

@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

@pytest.fixture
def sample_project():
    with TestingSessionLocal() as db:
        project = Project(
            name="Sample Project",
            status="Planned",
            progress=0,
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return {
            "id": project.id,
            "name": project.name,
            "status": project.status,
            "progress": project.progress,
        }