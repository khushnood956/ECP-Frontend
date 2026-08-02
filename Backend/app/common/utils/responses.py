from typing import Any, Optional
from fastapi.responses import JSONResponse
from app.common.schemas.responses import SuccessResponse, ErrorResponse
from app.core.logging.logger import request_id_ctx_var


def success_response(
    message: str = "Success",
    data: Any = None,
    status_code: int = 200,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    Constructs a standardized JSONResponse for successful operations.
    """
    if not request_id:
        request_id = request_id_ctx_var.get()
    
    response_model = SuccessResponse(
        success=True,
        message=message,
        data=data,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status_code,
        content=response_model.model_dump()
    )


def error_response(
    message: str,
    error_code: str,
    details: Optional[dict] = None,
    status_code: int = 500,
    request_id: Optional[str] = None
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
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status_code,
        content=response_model.model_dump()
    )
