from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import models  # noqa: F401
from app.api.routers import projects, tags, tasks, users
from app.core.exceptions import AppError

app = FastAPI(title="TaskHub API")

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(tags.router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers)


@app.get("/")
def root():
    return {"message": "TaskHub API is running"}
