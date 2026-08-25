"""
NIVAG AI Business Automation
Database Session Management

Production SQLAlchemy 2.x database engine and session factory.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


def _build_async_database_url(database_url: str) -> str:
    """
    Convert the configured PostgreSQL URL to SQLAlchemy's
    async psycopg driver URL.
    """

    if database_url.startswith("postgresql+psycopg://"):
        return database_url

    if database_url.startswith("postgresql://"):
        return database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    raise ValueError(
        "DATABASE_URL must use PostgreSQL with the psycopg driver."
    )


DATABASE_URL = _build_async_database_url(
    settings.database_url,
)


engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=1800,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a request-scoped asynchronous database session.

    Successful requests commit their database transaction.
    Failed requests are rolled back before the exception
    propagates to the application.
    """

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def dispose_database() -> None:
    """
    Dispose the SQLAlchemy engine during application shutdown.
    """

    await engine.dispose()


__all__ = [
    "AsyncSessionLocal",
    "DATABASE_URL",
    "dispose_database",
    "engine",
    "get_db_session",
]