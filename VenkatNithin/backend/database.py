"""
backend/database.py
-------------------
Database connection module for the Construction Intelligent Hub.

Provides three database backends:
- **SQLite** (via SQLAlchemy) — used in development and for relational data.
- **MongoDB** (via Motor) — async document store, used in production.
- **Redis** — optional cache / pub-sub layer; app continues without it.

Usage
-----
FastAPI dependency injection (SQLite session)::

    from fastapi import Depends
    from sqlalchemy.orm import Session
    from backend.database import get_db

    @router.get("/items")
    def list_items(db: Session = Depends(get_db)):
        ...

MongoDB (async)::

    from backend.database import get_mongo_db

    @router.get("/documents")
    async def list_docs():
        db = await get_mongo_db()
        return await db["collection"].find().to_list(100)

Application startup / shutdown (in main.py)::

    from backend.database import init_db, close_mongo

    @app.on_event("startup")
    async def startup():
        init_db()

    @app.on_event("shutdown")
    async def shutdown():
        await close_mongo()
"""

from __future__ import annotations

import logging
import os
from typing import AsyncGenerator, Generator, Optional

import redis
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SQLAlchemy — SQLite (development / relational data)
# ---------------------------------------------------------------------------

engine = create_engine(
    settings.database_url,
    # Required for SQLite when used with FastAPI's multi-threaded request
    # handling — each request runs in its own thread.
    connect_args={"check_same_thread": False},
)

SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy ``Session``.

    The session is always closed in the ``finally`` block, even if an
    exception is raised inside the route handler.

    Example::

        @router.get("/items")
        def list_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Motor — MongoDB (production / document store)
# ---------------------------------------------------------------------------

motor_client: Optional[AsyncIOMotorClient] = None  # lazy-initialised


async def get_mongo_db() -> AsyncIOMotorDatabase:
    """
    Return the Motor ``AsyncIOMotorDatabase`` instance for ``construction_hub``.

    The ``AsyncIOMotorClient`` is created lazily on the first call and reused
    on subsequent calls (connection-pool semantics).

    Raises
    ------
    ConnectionError
        Propagated from Motor if the MongoDB server is unreachable.
    """
    global motor_client

    if motor_client is None:
        try:
            motor_client = AsyncIOMotorClient(settings.mongo_uri)
            logger.info("Motor MongoDB client initialised.")
        except Exception as exc:  # pragma: no cover
            logger.error("Failed to create MongoDB client: %s", exc)
            raise

    return motor_client["construction_hub"]


async def close_mongo() -> None:
    """
    Close the Motor client connection pool.

    Should be called during application shutdown::

        @app.on_event("shutdown")
        async def shutdown():
            await close_mongo()
    """
    global motor_client

    if motor_client is not None:
        motor_client.close()
        motor_client = None
        logger.info("Motor MongoDB client closed.")


# ---------------------------------------------------------------------------
# Redis — optional cache / pub-sub
# ---------------------------------------------------------------------------

redis_client: Optional[redis.Redis] = None  # lazy-initialised


def get_redis() -> Optional[redis.Redis]:
    """
    Return a Redis client, creating it lazily on first call.

    If Redis is unavailable (e.g. in a minimal dev environment) the function
    logs a warning and returns ``None`` so callers can degrade gracefully
    instead of crashing.

    Returns
    -------
    redis.Redis | None
        A connected Redis client, or ``None`` if the connection failed.

    Example::

        cache = get_redis()
        if cache:
            cache.set("key", "value", ex=3600)
    """
    global redis_client

    if redis_client is not None:
        return redis_client

    try:
        client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
        )
        # Ping to verify the connection is actually alive before caching it.
        client.ping()
        redis_client = client
        logger.info("Redis client connected at %s.", settings.redis_url)
    except redis.exceptions.ConnectionError as exc:
        logger.warning(
            "Redis unavailable — continuing without cache. (%s)", exc
        )
        return None
    except Exception as exc:  # pragma: no cover
        logger.warning("Redis initialisation error — continuing without cache. (%s)", exc)
        return None

    return redis_client


# ---------------------------------------------------------------------------
# Database initialisation
# ---------------------------------------------------------------------------


def init_db() -> None:
    """
    Initialise all local storage resources required by the application.

    Specifically this function:

    1. Creates all SQLAlchemy / SQLite tables declared via ``Base.metadata``
       (models must be imported before this is called so their metadata is
       registered — ``main.py`` handles this via the model imports).
    2. Ensures the ``./data/uploads`` and ``./data/faiss_indexes`` directories
       exist, creating them (and any missing parents) if necessary.

    Call this once during application startup::

        @app.on_event("startup")
        async def startup():
            init_db()
    """
    # 1. Create SQLite tables
    logger.info("Creating SQLite tables (if not already present).")
    Base.metadata.create_all(bind=engine)

    # 2. Ensure required data directories exist
    required_dirs = [
        settings.upload_dir,       # ./data/uploads
        settings.faiss_index_dir,  # ./data/faiss_indexes
    ]

    for directory in required_dirs:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info("Directory ready: %s", directory)
        except OSError as exc:  # pragma: no cover
            logger.error("Could not create directory %s: %s", directory, exc)
            raise

    logger.info("Database initialisation complete.")
