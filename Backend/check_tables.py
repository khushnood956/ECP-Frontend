import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config.settings import settings

async def list_tables():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text('SHOW TABLES;'))
        tables = result.fetchall()
        print("Tables in database:", [t[0] for t in tables])
    await engine.dispose()

asyncio.run(list_tables())
