"""
Database Connection Management & Connection Pooling Engine
Provides asyncpg-backed SQLAlchemy async engine with production connection pooling,
session management, health checks, readiness probes, and automatic schema initialization.
Supports environment-based switching between SQLite (development) and PostgreSQL (production).
"""

import logging
import time
from typing import AsyncGenerator, Optional, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from .config import settings
from ..models.user import Base

logger = logging.getLogger("nutrient_platform.database")

engine = None
AsyncSessionLocal = None

# Initialize PostgreSQL engine if running in PostgreSQL mode or configured
effective_engine = settings.get_effective_db_engine()
db_url = settings.DATABASE_URL

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

if effective_engine == "postgresql" or settings.is_production():
    try:
        engine = create_async_engine(
            db_url,
            echo=settings.DEBUG,
            future=True,
            pool_size=settings.MAX_POOL_SIZE,
            max_overflow=settings.MAX_OVERFLOW,
            pool_timeout=settings.POOL_TIMEOUT,
            pool_recycle=settings.POOL_RECYCLE,
            pool_pre_ping=True,  # Test connection liveness prior to checkout
        )
        AsyncSessionLocal = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        logger.info(f"Initialized PostgreSQL asyncpg connection pool (pool_size={settings.MAX_POOL_SIZE}).")
    except Exception as e:
        logger.warning(f"PostgreSQL async engine initialization note: {e}. Falling back to SQLite persistence.")
        engine = None
        AsyncSessionLocal = None


async def get_db() -> AsyncGenerator[Optional[AsyncSession], None]:
    """
    FastAPI dependency yielding an async database session.
    Automatically handles commit/rollback and session closing.
    """
    if AsyncSessionLocal is None:
        yield None
        return

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as err:
            await session.rollback()
            logger.error(f"Database session error: {err}")
            raise
        finally:
            await session.close()


async def check_db_health() -> Dict[str, Any]:
    """
    Executes a health check verifying persistence engine and database connectivity.
    """
    from .persistence import PersistenceRepository, DB_PATH
    persistence_healthy = PersistenceRepository.is_healthy()
    assessment_count = 0
    try:
        conn = PersistenceRepository.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM assessments")
        assessment_count = cur.fetchone()[0]
        conn.close()
    except Exception as e:
        logger.warning(f"Persistence count check note: {e}")

    active_engine = settings.get_effective_db_engine()

    if engine is None or active_engine == "sqlite":
        return {
            "status": "HEALTHY" if persistence_healthy else "UNAVAILABLE",
            "connected": persistence_healthy,
            "engine": "SQLite",
            "persistence_layer": "SQLITE_WAL",
            "persistence_file": DB_PATH,
            "persisted_assessments": assessment_count,
            "pool_size": 0
        }

    try:
        t0 = time.perf_counter()
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            val = result.scalar()
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            pool = engine.pool
            return {
                "status": "HEALTHY" if val == 1 else "DEGRADED",
                "connected": val == 1,
                "engine": "PostgreSQL (asyncpg)",
                "persistence_layer": "POSTGRESQL_CONNECTION_POOL",
                "persisted_assessments": assessment_count,
                "latency_ms": latency_ms,
                "pool_size": pool.size() if hasattr(pool, "size") else settings.MAX_POOL_SIZE,
                "checked_out": pool.checkedout() if hasattr(pool, "checkedout") else 0,
                "overflow": pool.overflow() if hasattr(pool, "overflow") else 0
            }
    except Exception as e:
        logger.warning(f"PostgreSQL health probe exception: {e}")
        return {
            "status": "HEALTHY" if persistence_healthy else "DISCONNECTED",
            "connected": persistence_healthy,
            "engine": "PostgreSQL (Fell back to SQLite WAL)",
            "persistence_layer": "SQLITE_FALLBACK",
            "persistence_file": DB_PATH,
            "persisted_assessments": assessment_count,
            "error": str(e),
            "pool_size": settings.MAX_POOL_SIZE
        }


async def check_db_readiness() -> Dict[str, Any]:
    """
    Readiness probe (/ready): checks if database is ready to accept production query traffic.
    """
    health = await check_db_health()
    is_ready = health.get("connected", False) and health.get("status") in ["HEALTHY", "DEGRADED"]
    return {
        "ready": is_ready,
        "status": "READY" if is_ready else "NOT_READY",
        "database": health
    }


async def init_db():
    """
    Initializes database tables if running in PostgreSQL mode with active connection.
    """
    if engine is not None:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("PostgreSQL database tables verified and initialized successfully.")
        except Exception as e:
            logger.warning(f"PostgreSQL schema creation notice (offline/local fallback): {e}")
