"""
NIVAG AI Business Automation
Pytest Configuration

Shared asynchronous PostgreSQL test fixtures.
"""

from __future__ import annotations

import asyncio
import selectors
from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base.base import Base
from app.db.session.database import engine


def postgres_event_loop() -> asyncio.AbstractEventLoop:
    """
    Create a selector-based event loop for PostgreSQL async tests.

    Psycopg's asynchronous driver does not support the Windows
    ProactorEventLoop. A selector-based loop is required on Windows.
    """

    return asyncio.SelectorEventLoop(
        selectors.SelectSelector(),
    )


def pytest_asyncio_loop_factories(config, item):
    """
    Provide the selector-based event loop factory for pytest-asyncio.
    """

    return {
        "postgres": postgres_event_loop,
    }


async def _clean_database(
    session: AsyncSession,
) -> None:
    """
    Remove all application data from the PostgreSQL test database.

    This fixture is intentionally destructive and must only be used
    against the configured test database.
    """

    tables = list(Base.metadata.sorted_tables)

    if not tables:
        return

    table_names = ", ".join(
        f'"{table.schema}"."{table.name}"'
        if table.schema
        else f'"{table.name}"'
        for table in tables
    )

    await session.execute(
        text(
            f"TRUNCATE TABLE {table_names} "
            "RESTART IDENTITY CASCADE"
        )
    )

    await session.commit()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an isolated asynchronous PostgreSQL test session.

    Application services own transaction boundaries and may commit
    transactions. Database cleanup is performed before and after
    each test.
    """

    async with engine.connect() as connection:
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        try:
            await _clean_database(session)

            yield session

        finally:
            try:
                await session.rollback()
                await _clean_database(session)
            finally:
                await session.close()


__all__ = [
    "db_session",
    "postgres_event_loop",
    "pytest_asyncio_loop_factories",
]