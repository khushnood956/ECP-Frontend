from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, Callable

from app.db.session import get_db
from app.repositories.transaction import TransactionManager

# Reuse the existing database/session implementation directly
# Typing explicitly as a dependency generator for clarity in downstream providers
get_db_session: Callable[[], AsyncGenerator[AsyncSession, None]] = get_db

def get_transaction_manager(
    session: AsyncSession = Depends(get_db_session)
) -> TransactionManager:
    """
    Dependency provider for TransactionManager.
    Receives the current request's AsyncSession via FastAPI DI.
    """
    return TransactionManager(session)
