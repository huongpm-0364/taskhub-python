from fastapi import FastAPI

from app import models  # noqa: F401
from app.routers import projects, tasks, users

app = FastAPI(title="TaskHub API")

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.get("/")
def root():
    return {"message": "TaskHub API is running"}
