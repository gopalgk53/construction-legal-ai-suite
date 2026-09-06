from fastapi import FastAPI

from routes.milestones import router as milestones_router
from routes.projects import router as projects_router
from routes.tasks import router as tasks_router

app = FastAPI(
    title="AI Portfolio Commander",
    version="1.0"
)
app.include_router(projects_router)
app.include_router(milestones_router)
app.include_router(tasks_router)


@app.get("/")
def home():
    return {
        "message": "AI Portfolio Commander"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/about")
def about():
    return {
        "project": "AI Portfolio Commander",
        "version": "1.0"
    }


