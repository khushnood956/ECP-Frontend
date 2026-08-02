import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config.settings import settings

async def reset_db():
    base_url = settings.DATABASE_URL.rsplit('/', 1)[0]
    engine = create_async_engine(base_url)
    try:
        async with engine.connect() as conn:
            await conn.execute(text('DROP DATABASE IF EXISTS educonsultant'))
            await conn.execute(text('CREATE DATABASE educonsultant'))
            print("Successfully reset database educonsultant.")
    except Exception as e:
        print(f"Failed to reset db: {e}")
    finally:
        await engine.dispose()

asyncio.run(reset_db())
