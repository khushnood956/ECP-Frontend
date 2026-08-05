from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.config.constants import API_V1_PREFIX
from app.core.config.enums import Environment


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables or .env file.
    Fail-fast validation is provided by pydantic.
    """

    # Project
    PROJECT_NAME: str = "EduConsultant"
    PROJECT_VERSION: str = "0.1.0"
    API_PREFIX: str = API_V1_PREFIX
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = Field(..., description="MySQL Database connection URL (async)")

    # Redis
    REDIS_URL: str = Field(..., description="Redis connection URL")

    # Security
    SECRET_KEY: str = Field(..., description="Secret key for JWT generation")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # CORS
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, env_file_encoding="utf-8", extra="ignore"
    )


# Singleton instance of settings
settings = Settings()
