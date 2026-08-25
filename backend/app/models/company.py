"""
==========================================================
NIVAG AI Business Automation

Company Model

Tenant-scoped CRM company entity.

A company belongs to exactly one organization. All company
queries must be scoped by organization_id to preserve
multi-tenant isolation.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base.base import Base
from app.db.base.model_mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class Company(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """
    Represents a business company inside a single organization.

    The organization_id defines the tenant boundary. Company records
    must never be queried or modified outside their owning organization.
    """

    __tablename__ = "companies"

    __table_args__ = (
        Index(
            "ix_companies_organization_name",
            "organization_id",
            "name",
        ),
        Index(
            "ix_companies_organization_email",
            "organization_id",
            "email",
        ),
        Index(
            "ix_companies_organization_website",
            "organization_id",
            "website",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    legal_name: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(320),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    website: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    industry: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    address_line_1: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    address_line_2: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    postal_code: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="companies",
        lazy="raise",
    )

    def __repr__(self) -> str:
        """Return a safe developer-facing representation."""

        return (
            "<Company("
            f"id={self.id!s}, "
            f"organization_id={self.organization_id!s}, "
            f"name={self.name!r}"
            ")>"
        )


__all__ = [
    "Company",
]