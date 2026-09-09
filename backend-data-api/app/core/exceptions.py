from fastapi import Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail


class MLServiceError(Exception):
    def __init__(self, detail: str = "ML service unavailable"):
        self.detail = detail


async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.detail})


async def ml_service_error_handler(request: Request, exc: MLServiceError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": exc.detail})


def register_exception_handlers(app) -> None:
    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(MLServiceError, ml_service_error_handler)
