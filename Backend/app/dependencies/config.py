from fastapi import Depends
from app.core.config.settings import Settings, settings

def get_settings() -> Settings:
    """
    Dependency injection for application settings.
    Allows easy mocking in tests and explicit dependency tracing in routers and services.
    
    Returns:
        Settings: The singleton settings instance.
    """
    return settings
