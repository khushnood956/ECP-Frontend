from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.common.schemas.responses import ErrorResponse, SuccessResponse
from app.core.logging.logger import request_id_ctx_var


def success_response(
    message: str = "Success",
    data: Any = None,
    status_code: int = 200,
    request_id: str | None = None,
) -> JSONResponse:
    """
    Constructs a standardized JSONResponse for successful operations.
    """
    if not request_id:
        request_id = request_id_ctx_var.get()

    response_model = SuccessResponse(
        success=True, message=message, data=data, request_id=request_id
    )

    return JSONResponse(
        status_code=status_code, content=jsonable_encoder(response_model)
    )


def error_response(
    message: str,
    error_code: str,
    details: dict | None = None,
    status_code: int = 500,
    request_id: str | None = None,
) -> JSONResponse:
    """
    Constructs a standardized JSONResponse for failed operations.
    """
    if not request_id:
        request_id = request_id_ctx_var.get()

    response_model = ErrorResponse(
        success=False,
        message=message,
        error_code=error_code,
        details=details or {},
        request_id=request_id,
    )

    return JSONResponse(
        status_code=status_code, content=jsonable_encoder(response_model)
    )
