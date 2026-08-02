import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config.settings import settings

async def test_db():
    engine = create_async_engine(settings.DATABASE_URL)
    try:
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
            print("Successfully connected to the database.")
    except Exception as e:
        print(f"Failed to connect: {e}")
    finally:
        await engine.dispose()

asyncio.run(test_db())
