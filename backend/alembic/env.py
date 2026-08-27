"""
NIVAG AI Business Automation
Alembic Migration Environment
"""

from __future__ import annotations

import asyncio
import selectors
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.db.base.base import Base
from app.models.activity import Activity  # noqa: F401
from app.models.company import Company  # noqa: F401
from app.models.contact import Contact  # noqa: F401
from app.models.lead import Lead  # noqa: F401
from app.models.opportunity import Opportunity  # noqa: F401
from app.models.organization import Organization  # noqa: F401
from app.models.user import User  # noqa: F401


config = context.config


if config.config_file_name is not None:
    fileConfig(
        config.config_file_name,
    )


target_metadata = Base.metadata


def get_database_url() -> str:
    """Return the database URL from the application configuration."""

    return settings.database_url


def run_migrations_offline() -> None:
    """Run migrations without creating a database connection."""

    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(
    connection: Connection,
) -> None:
    """Configure and execute migrations using an active connection."""

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run Alembic migrations through SQLAlchemy's async engine."""

    configuration = (
        config.get_section(
            config.config_ini_section,
        )
        or {}
    )

    configuration["sqlalchemy.url"] = (
        get_database_url()
    )

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    try:
        async with connectable.connect() as connection:
            await connection.run_sync(
                do_run_migrations,
            )
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations against the configured database.

    Psycopg's asynchronous interface requires a selector-based
    event loop on Windows.
    """

    asyncio.run(
        run_async_migrations(),
        loop_factory=lambda: asyncio.SelectorEventLoop(
            selectors.SelectSelector(),
        ),
    )


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()