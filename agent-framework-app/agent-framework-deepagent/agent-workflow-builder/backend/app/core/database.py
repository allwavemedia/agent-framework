"""
Database configuration and initialization.
"""
import logging
from typing import AsyncGenerator

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create database engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )
    async_engine = None
else:
    # PostgreSQL or other async database
    async_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
    )
    engine = None

# Create session factory
if async_engine:
    AsyncSessionLocal = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    SessionLocal = None
else:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    AsyncSessionLocal = None


async def init_db() -> None:
    """Initialize the database."""
    try:
        if async_engine:
            async with async_engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
        else:
            SQLModel.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    if not AsyncSessionLocal:
        raise RuntimeError("Async session not configured")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_session() -> Session:
    """Get synchronous database session."""
    if not SessionLocal:
        raise RuntimeError("Sync session not configured")
    
    with SessionLocal() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Choose the appropriate session getter based on database type
if async_engine:
    get_db = get_async_session
else:
    get_db = get_session