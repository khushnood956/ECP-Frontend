from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an asynchronous database session.
    Automatically handles commit, rollback on exceptions, and closing the session.
    Yields:
        AsyncSession: The database session object.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # We don't automatically commit here, repositories should commit explicitly.
            # But the session will be closed automatically when exiting the context manager.
        except Exception as exc:
            logger.error(f"Database session rollback due to exception: {exc}")
            await session.rollback()
            raise
