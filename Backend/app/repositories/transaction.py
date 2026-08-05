from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging.logger import get_logger
from app.repositories.exceptions import RepositoryError

logger = get_logger(__name__)


class TransactionManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[None, None]:
        """
        Async context manager for managing transactions.
        Commits on success, rollbacks on exception.
        """
        try:
            yield
            await self.session.commit()
        except Exception as e:
            logger.error(f"Transaction rollback due to exception: {e}")
            await self.session.rollback()
            if isinstance(e, SQLAlchemyError):
                raise RepositoryError(
                    "Database transaction error", details={"error": str(e)}
                ) from e
            raise
