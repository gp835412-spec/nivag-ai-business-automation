"""
NIVAG AI Business Automation
Organization Model

Tenant root entity for the multi-tenant business platform.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base.base import Base
from app.db.base.model_mixins import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.contact import Contact
    from app.models.lead import Lead
    from app.models.opportunity import Opportunity
    from app.models.user import User


class OrganizationStatus(StrEnum):
    """Lifecycle status of an organization."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class Organization(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """
    Represents an independent business tenant.

    All tenant-owned resources reference this entity
    through organization_id.
    """

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
        index=True,
    )

    legal_name: Mapped[str | None] = mapped_column(
        String(200),
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

    timezone: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="Asia/Kolkata",
        server_default="Asia/Kolkata",
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR",
        server_default="INR",
    )

    status: Mapped[OrganizationStatus] = mapped_column(
        String(20),
        nullable=False,
        default=OrganizationStatus.ACTIVE,
        server_default=OrganizationStatus.ACTIVE.value,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="organization",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
    )

    companies: Mapped[list["Company"]] = relationship(
        "Company",
        back_populates="organization",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
    )

    contacts: Mapped[list["Contact"]] = relationship(
        "Contact",
        back_populates="organization",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
    )

    leads: Mapped[list["Lead"]] = relationship(
        "Lead",
        back_populates="organization",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
    )

    opportunities: Mapped[list["Opportunity"]] = relationship(
        "Opportunity",
        back_populates="organization",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
    )


__all__ = [
    "Organization",
    "OrganizationStatus",
]