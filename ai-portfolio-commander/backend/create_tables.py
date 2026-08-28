from database.connection import engine
from database.base import Base

from models.project import Project

print("Tables Registered:")
print(Base.metadata.tables.keys())

print("Creating tables...")

Base.metadata.create_all(bind=engine)

print("✅ Tables Created")