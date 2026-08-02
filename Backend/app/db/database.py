from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from app.core.config.settings import settings

# Create the AsyncEngine
# Note: The underlying engine adapts to settings.DATABASE_URL dynamically.
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,       # Validates connections before usage
    pool_recycle=3600,        # Recycles connections every hour to prevent staleness
    pool_size=5,              # Base connection pool size
    max_overflow=10           # Max additional connections beyond pool_size
)

# Create the async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,   # Prevents DetachedInstanceError after commit
    autocommit=False,
    autoflush=False
)
