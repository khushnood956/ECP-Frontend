from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions.base import ApplicationException
from app.common.utils.responses import error_response
from app.core.logging.logger import get_logger

logger = get_logger(__name__)

def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers global exception handlers for the FastAPI application.
    Prevents stack traces from being leaked to the client while logging them internally.
    """

    @app.exception_handler(ApplicationException)
    async def application_exception_handler(request: Request, exc: ApplicationException):
        req_id = getattr(request.state, "request_id", None)
        logger.warning(f"Application exception: {exc.error_code} - {exc.message}")
        return error_response(
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
            status_code=exc.status_code,
            request_id=req_id
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        req_id = getattr(request.state, "request_id", None)
        logger.warning(f"Validation error on {request.url}: {exc.errors()}")
        return error_response(
            message="Request validation failed.",
            error_code="VALIDATION_ERROR",
            details={"errors": exc.errors()},
            status_code=422,
            request_id=req_id
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        req_id = getattr(request.state, "request_id", None)
        logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
        return error_response(
            message=str(exc.detail),
            error_code="HTTP_ERROR",
            status_code=exc.status_code,
            request_id=req_id
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        req_id = getattr(request.state, "request_id", None)
        logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
        return error_response(
            message="An unexpected error occurred.",
            error_code="INTERNAL_SERVER_ERROR",
            status_code=500,
            request_id=req_id
        )
