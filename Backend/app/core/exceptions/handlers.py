from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.common.utils.responses import error_response
from app.core.exceptions.base import ApplicationException
from app.core.logging.logger import get_logger
from app.services.exceptions import (
    BusinessRuleViolation,
    EntityAlreadyExists,
    EntityNotFound,
    PermissionDenied,
    ValidationFailure,
)

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers global exception handlers for the FastAPI application.
    Prevents stack traces from being leaked to the client while logging them internally.
    """

    @app.exception_handler(ApplicationException)
    async def application_exception_handler(
        request: Request, exc: ApplicationException
    ):
        req_id = getattr(request.state, "request_id", None)
        logger.warning(f"Application exception: {exc.error_code} - {exc.message}")
        return error_response(
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
            status_code=exc.status_code,
            request_id=req_id,
        )

    @app.exception_handler(EntityNotFound)
    async def entity_not_found_handler(request: Request, exc: EntityNotFound):
        req_id = getattr(request.state, "request_id", None)
        logger.warning(f"Entity not found: {exc.message}")
        return error_response(
            message=exc.message,
            error_code="NOT_FOUND",
            details=exc.details,
            status_code=404,
            request_id=req_id,
        )

    @app.exception_handler(BusinessRuleViolation)
    async def business_rule_violation_handler(
        request: Request, exc: BusinessRuleViolation
    ):
        req_id = getattr(request.state, "request_id", None)
        logger.warning(f"Business rule violation: {exc.message}")
        return error_response(
            message=exc.message,
            error_code="BUSINESS_RULE_VIOLATION",
            details=exc.details,
            status_code=400,
            request_id=req_id,
        )

    @app.exception_handler(EntityAlreadyExists)
    async def entity_already_exists_handler(request: Request, exc: EntityAlreadyExists):
        req_id = getattr(request.state, "request_id", None)
        logger.warning(f"Entity already exists: {exc.message}")
        return error_response(
            message=exc.message,
            error_code="CONFLICT",
            details=exc.details,
            status_code=409,
            request_id=req_id,
        )

    @app.exception_handler(PermissionDenied)
    async def permission_denied_handler(request: Request, exc: PermissionDenied):
        req_id = getattr(request.state, "request_id", None)
        logger.warning(f"Permission denied: {exc.message}")
        return error_response(
            message=exc.message,
            error_code="FORBIDDEN",
            details=exc.details,
            status_code=403,
            request_id=req_id,
        )

    @app.exception_handler(ValidationFailure)
    async def validation_failure_handler(request: Request, exc: ValidationFailure):
        req_id = getattr(request.state, "request_id", None)
        logger.warning(f"Validation failure: {exc.message}")
        return error_response(
            message=exc.message,
            error_code="VALIDATION_ERROR",
            details=exc.details,
            status_code=422,
            request_id=req_id,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        req_id = getattr(request.state, "request_id", None)
        logger.warning(f"Validation error on {request.url}: {exc.errors()}")
        return error_response(
            message="Request validation failed.",
            error_code="VALIDATION_ERROR",
            details={"errors": exc.errors()},
            status_code=422,
            request_id=req_id,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        req_id = getattr(request.state, "request_id", None)
        logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
        return error_response(
            message=str(exc.detail),
            error_code="HTTP_ERROR",
            status_code=exc.status_code,
            request_id=req_id,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        req_id = getattr(request.state, "request_id", None)
        logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
        return error_response(
            message="An unexpected error occurred.",
            error_code="INTERNAL_SERVER_ERROR",
            status_code=500,
            request_id=req_id,
        )
