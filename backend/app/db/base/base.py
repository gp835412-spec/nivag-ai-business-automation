"""
NIVAG AI Business Automation
SQLAlchemy Declarative Base
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from app.db.base.model_mixins import TimestampMixin


NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Root declarative base for all NIVAG database models.
    """

    metadata = MetaData(
        naming_convention=NAMING_CONVENTION,
    )


__all__ = [
    "Base",
    "TimestampMixin",
]