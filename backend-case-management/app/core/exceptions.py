from fastapi import Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail


class MLServiceError(Exception):
    def __init__(self, detail: str = "ML service unavailable"):
        self.detail = detail


import logging

logger = logging.getLogger(__name__)

async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.detail})

async def ml_service_error_handler(request: Request, exc: MLServiceError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": exc.detail})

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500, 
        content={"detail": "An internal server error occurred. Please try again later."}
    )

def register_exception_handlers(app) -> None:
    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(MLServiceError, ml_service_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
