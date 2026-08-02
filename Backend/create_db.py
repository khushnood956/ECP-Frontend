import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config.settings import settings

async def create_db():
    # Remove the DB name from the URL
    base_url = settings.DATABASE_URL.rsplit('/', 1)[0]
    engine = create_async_engine(base_url)
    try:
        async with engine.connect() as conn:
            await conn.execute(text('CREATE DATABASE IF NOT EXISTS educonsultant'))
            print("Successfully created database educonsultant.")
    except Exception as e:
        print(f"Failed to create db: {e}")
    finally:
        await engine.dispose()

asyncio.run(create_db())
