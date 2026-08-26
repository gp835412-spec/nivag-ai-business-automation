"""
==========================================================
NIVAG AI Business Automation

Contact Model

Tenant-scoped CRM contact entity.

A contact always belongs to an organization and may
optionally be associated with a company.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base.base import Base
from app.db.base.model_mixins import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.organization import Organization


class Contact(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """
    Represents a CRM contact inside an organization.

    Every contact belongs to exactly one organization.

    A contact may optionally be associated with a company
    belonging to the same organization.
    """

    __tablename__ = "contacts"

    __table_args__ = (
        Index(
            "ix_contacts_organization_email",
            "organization_id",
            "email",
        ),
        Index(
            "ix_contacts_organization_name",
            "organization_id",
            "last_name",
            "first_name",
        ),
        Index(
            "ix_contacts_organization_company_id",
            "organization_id",
            "company_id",
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

    company_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "companies.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str | None] = mapped_column(
        String(100),
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

    job_title: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    department: Mapped[str | None] = mapped_column(
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
        back_populates="contacts",
        lazy="raise",
    )

    company: Mapped["Company | None"] = relationship(
        "Company",
        back_populates="contacts",
        lazy="raise",
    )


__all__ = [
    "Contact",
]