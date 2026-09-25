class AppError(Exception):
    """Base for domain/application errors that map directly to an HTTP response.

    Raise a subclass of this anywhere below the router (service, dependency,
    repository) and the handler registered in app/main.py converts it into a
    consistent `{"detail": "..."}` JSON response with the right status code —
    callers don't need their own try/except + HTTPException boilerplate at every
    call site, and every error response shares the same shape.
    """

    status_code: int = 400
    detail: str = "Application error"

    def __init__(self, detail: str | None = None, *, headers: dict[str, str] | None = None):
        if detail is not None:
            self.detail = detail
        self.headers = headers
        super().__init__(self.detail)


class BadRequestError(AppError):
    status_code = 400


class UnauthorizedError(AppError):
    status_code = 401


class ForbiddenError(AppError):
    status_code = 403


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409
