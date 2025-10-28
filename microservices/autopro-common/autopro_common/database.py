"""
Async SQLAlchemy database utilities with connection pooling
"""
import os
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import text

from .logging import get_logger

logger = get_logger(__name__)

# Base class for all models
Base = declarative_base()


class AsyncDatabase:
    """Async database connection manager"""

    def __init__(
        self,
        database_url: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False,
    ):
        """
        Initialize async database connection
        
        Args:
            database_url: PostgreSQL connection URL (must start with postgresql+asyncpg://)
            pool_size: Number of permanent connections
            max_overflow: Max temporary connections above pool_size
            pool_timeout: Timeout for getting connection from pool
            pool_recycle: Recycle connections after this many seconds
            echo: Log all SQL queries
        """
        # Convert postgres:// to postgresql+asyncpg://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        self.database_url = database_url
        
        # Create async engine with connection pooling
        self.engine: AsyncEngine = create_async_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            echo=echo,
            future=True,
        )
        
        # Create session factory
        self.async_session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        logger.info(f"Database initialized with pool_size={pool_size}")

    async def test_connection(self) -> bool:
        """
        Test database connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session context manager
        
        Usage:
            async with db.session() as session:
                result = await session.execute(query)
        """
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def create_tables(self) -> None:
        """Create all tables defined in Base metadata"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

    async def drop_tables(self) -> None:
        """Drop all tables defined in Base metadata"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("Database tables dropped")

    async def close(self) -> None:
        """Close database connection pool"""
        await self.engine.dispose()
        logger.info("Database connection pool closed")


# Global database instance
_db_instance: Optional[AsyncDatabase] = None


def init_database(
    database_url: Optional[str] = None,
    pool_size: int = 10,
    **kwargs
) -> AsyncDatabase:
    """
    Initialize global database instance
    
    Args:
        database_url: Database URL (defaults to DATABASE_URL env var)
        pool_size: Connection pool size
        **kwargs: Additional arguments for AsyncDatabase
        
    Returns:
        Initialized AsyncDatabase instance
    """
    global _db_instance
    
    if database_url is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            # Fallback to Supabase URL
            supabase_url = os.getenv("SUPABASE_URL", "")
            if supabase_url:
                # Extract project ref from URL
                import re
                match = re.search(r"https://([^.]+)\.supabase\.co", supabase_url)
                if match:
                    project_ref = match.group(1)
                    database_url = f"postgresql://postgres:postgres@db.{project_ref}.supabase.co:5432/postgres"
    
    if not database_url:
        raise ValueError("DATABASE_URL or SUPABASE_URL environment variable required")
    
    _db_instance = AsyncDatabase(database_url, pool_size=pool_size, **kwargs)
    return _db_instance


def get_database() -> AsyncDatabase:
    """
    Get global database instance
    
    Returns:
        AsyncDatabase instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    if _db_instance is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _db_instance


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db_session)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    db = get_database()
    async with db.session() as session:
        yield session
