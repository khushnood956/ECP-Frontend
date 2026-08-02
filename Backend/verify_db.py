import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config.settings import settings

async def verify_db():
    engine = create_async_engine(settings.DATABASE_URL)
    try:
        async with engine.connect() as conn:
            # Tables
            tables = await conn.execute(text('SHOW TABLES'))
            print("TABLES:", [t[0] for t in tables.fetchall()])
            
            # Constraints
            for table in ['users', 'student_profiles', 'agencies', 'scholarships', 'leads']:
                print(f"\n--- {table.upper()} ---")
                columns = await conn.execute(text(f'SHOW COLUMNS FROM {table}'))
                print("COLUMNS:")
                for col in columns.fetchall():
                    print(f"  {col[0]}: Type={col[1]}, Null={col[2]}, Key={col[3]}, Default={col[4]}")
                
                indexes = await conn.execute(text(f'SHOW INDEX FROM {table}'))
                print("INDEXES:")
                for idx in indexes.fetchall():
                    print(f"  {idx[2]} (Column: {idx[4]}, Non_unique: {idx[1]})")
                
                fks = await conn.execute(text(f"SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = 'educonsultant' AND TABLE_NAME = '{table}' AND REFERENCED_TABLE_NAME IS NOT NULL"))
                print("FOREIGN KEYS:")
                for fk in fks.fetchall():
                    print(f"  {fk[0]} -> {fk[1]}.{fk[2]}")
                
    except Exception as e:
        print(f"Failed verification: {e}")
    finally:
        await engine.dispose()

asyncio.run(verify_db())
