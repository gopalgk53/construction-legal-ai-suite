from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database.dependency import get_db
from database.base import Base
from models.project import Project
import pytest


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


TEST_DATABASE_URL = (
    "postgresql://gopalakrishnagk53@localhost:5432/portfolio_test"
)


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
    db = TestingSessionLocal()

    project = Project(
        name="Sample Project",
        status="Planned",
        progress=0,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    project_data = {
        "id": project.id,
        "name": project.name,
        "status": project.status,
        "progress": project.progress,
    }

    db.close()

    return project_data
