import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.db.base import Base

from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.agency import Agency
from app.models.scholarship import Scholarship
from app.models.lead import Lead

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "mysql+aiomysql://root:admin@localhost:3306/educonsultant_test")

@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    yield eng
    await eng.dispose()

@pytest_asyncio.fixture(scope="session")
async def setup_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def db_session(engine, setup_db) -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()
        async_session = async_sessionmaker(
            conn, 
            class_=AsyncSession, 
            expire_on_commit=False, 
            join_transaction_mode="create_savepoint"
        )
        async with async_session() as session:
            yield session
        await conn.rollback()
