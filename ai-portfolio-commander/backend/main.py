from fastapi import FastAPI

app = FastAPI(
    title="AI Portfolio Commander",
    version="1.0"
)


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

