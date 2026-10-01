import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import models  # noqa: F401
from app.api.routers import projects, tags, tasks, users
from app.core import messages
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging_config import configure_logging

configure_logging()
logger = logging.getLogger("taskhub.errors")

app = FastAPI(title="TaskHub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(tags.router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers)


# Catches anything NOT already handled above (a real bug, not an expected AppError) —
# Starlette picks the most specific registered handler by walking the exception's MRO,
# so this only ever fires for exceptions with no more specific handler (this one included
# — FastAPI's own HTTPException/RequestValidationError handlers still take precedence).
# Logs the full traceback server-side but never leaks it to the client.
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": messages.INTERNAL_SERVER_ERROR})


@app.get("/")
def root():
    return {"message": "TaskHub API is running"}
