"""
Database Base Configuration
SQLAlchemy 엔진 및 세션 설정
"""

import logging
import os
from typing import Generator

from sqlalchemy import MetaData, create_engine, event, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

logger = logging.getLogger(__name__)

# Engine configuration based on environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
TESTING = os.getenv("TESTING", "false").lower() == "true"

# Database URL configuration
if TESTING:
    # Use SQLite for testing (no external dependencies)
    DATABASE_URL = "sqlite:///./test.db"
    ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/t_developer"
    )
    # Add async support
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

if ENVIRONMENT == "production":
    # Production settings with connection pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,  # Number of connections to maintain in pool
        max_overflow=40,  # Maximum overflow connections
        pool_pre_ping=True,  # Test connections before using
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=False,
        connect_args={
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000",  # 30 seconds statement timeout
        }
        if not TESTING
        else {},
    )
elif TESTING:
    # Testing with SQLite
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,
        echo=False,
        connect_args={"check_same_thread": False},  # SQLite specific
    )
else:
    # Development settings
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=True,  # Log SQL queries in development
        connect_args={"connect_timeout": 10},
    )

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,  # Don't expire objects after commit
)

# Metadata with naming convention for migrations
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

# Declarative base
Base = declarative_base(metadata=metadata)


# Event listeners for connection management
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set connection parameters"""
    if "sqlite" in DATABASE_URL:
        # SQLite specific settings
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    else:
        # PostgreSQL specific settings
        cursor = dbapi_conn.cursor()
        cursor.execute("SET timezone = 'UTC'")
        cursor.close()


@event.listens_for(engine, "checkout")
def ping_connection(dbapi_conn, connection_record, connection_proxy):
    """Ping connection to verify it's still valid"""
    if ENVIRONMENT == "production":
        try:
            # Test connection
            cursor = dbapi_conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
        except Exception as e:
            # Connection is broken, returning False will cause a reconnect
            logger.warning(f"Database connection lost: {e}")
            raise


# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI

    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# Async session support (for future)
try:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=ENVIRONMENT == "development",
        pool_pre_ping=True,
        pool_size=20 if ENVIRONMENT == "production" else 5,
    )

    AsyncSessionLocal = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def get_async_db() -> AsyncSession:
        """Async database session dependency"""
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

except ImportError:
    # asyncpg not installed
    async_engine = None
    AsyncSessionLocal = None
    get_async_db = None


# Database initialization
def init_db():
    """Initialize database tables"""
    # Import all models to register them with Base
    from . import models

    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_db():
    """Drop all database tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped!")


# Health check
def check_database_health() -> bool:
    """Check if database is accessible"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
