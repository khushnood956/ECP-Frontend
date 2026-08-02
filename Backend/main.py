import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config.settings import settings
from app.api.router import api_router
from app.core.logging.logger import get_logger
from app.middleware.request_id import RequestLoggingMiddleware
from app.core.exceptions.handlers import register_exception_handlers
from app.common.utils.responses import success_response
from app.common.schemas.responses import SuccessResponse

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    logger.info(f"--- Starting {settings.PROJECT_NAME} ---")
    logger.info(f"Environment: {settings.ENVIRONMENT.value.upper()}")
    logger.info(f"Version: {settings.PROJECT_VERSION}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info("---------------------------------------")
    
    yield
    
    logger.info(f"--- Shutting down {settings.PROJECT_NAME} ---")


def create_app() -> FastAPI:
    """
    Application factory for the FastAPI application.
    Configures CORS, middleware, global exceptions, and registers routers.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="EduConsultant Backend API",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        lifespan=lifespan
    )

    # Register Middlewares
    # The order of middleware matters. Add Request Logging first so it wraps everything.
    app.add_middleware(RequestLoggingMiddleware)

    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Register Global Exception Handlers
    register_exception_handlers(app)

    # Register API routers
    app.include_router(api_router, prefix=settings.API_PREFIX)

    @app.get("/health", tags=["System"], response_model=SuccessResponse)
    async def health_check() -> JSONResponse:
        """
        Basic health check endpoint to verify the service is running.
        Returns standardized success response.
        """
        logger.info("Health check endpoint accessed.")
        return success_response(
            message="Service is healthy and running.",
            data={"status": "ok"}
        )

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
