from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
from models import Base
import logging

logger = logging.getLogger(__name__)

# Create async engine for database operations
if settings.DATABASE_URL.startswith("sqlite"):
    # For SQLite in development
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
    engine_kwargs = {"echo": settings.DEBUG}
elif settings.DATABASE_URL.startswith("postgresql"):
    # For PostgreSQL
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine_kwargs = {
        "echo": settings.DEBUG,
        "pool_size": 20,
        "max_overflow": 0,
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
else:
    # Default to PostgreSQL format
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
    engine_kwargs = {"echo": settings.DEBUG}

# Async engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    future=True,
    **engine_kwargs
)

# Async session maker
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency to get database session
async def get_db():
    """Get database session dependency"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """Create all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

async def drop_tables():
    """Drop all database tables (use with caution!)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("Database tables dropped")

async def reset_database():
    """Reset database by dropping and recreating all tables"""
    await drop_tables()
    await create_tables()
    logger.info("Database reset completed")

# Connection management
async def connect_db():
    """Connect to the database"""
    # With SQLAlchemy async, connection is managed automatically
    logger.info("Database engine ready")

async def disconnect_db():
    """Disconnect from the database"""
    await engine.dispose()
    logger.info("Database engine disposed")

# Health check function
async def check_database_health():
    """Check if database is accessible"""
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False 