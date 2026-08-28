from database.session import SessionLocal
from models.project import Project

db = SessionLocal()

project = Project(
    name="AI Portfolio Commander",
    status="In Progress",
    progress=25
)

db.add(project)
db.commit()

print("✅ Project Added")