from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


async def check_database_health(db: AsyncSession) -> bool:
    """
    Performs a lightweight query to ensure the database is accessible.
    
    Args:
        db (AsyncSession): The active database session.
        
    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        await db.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}")
        return False
