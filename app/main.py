from fastapi import FastAPI

from app import models  # noqa: F401
from app.api.routers import projects, tags, tasks, users

app = FastAPI(title="TaskHub API")

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(tags.router)


@app.get("/")
def root():
    return {"message": "TaskHub API is running"}
