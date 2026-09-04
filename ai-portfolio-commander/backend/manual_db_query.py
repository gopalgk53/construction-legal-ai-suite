from database.session import SessionLocal
from models.project import Project

db = SessionLocal()

projects = db.query(Project).all()

print(f"Projects Found: {len(projects)}")

for project in projects:
    print(
        project.id,
        project.name,
        project.status,
        project.progress
    )