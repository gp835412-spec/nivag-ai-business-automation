"""
==========================================================
NIVAG AI Business Automation

Company Model

Tenant-scoped CRM company entity.

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
    from app.models.contact import Contact
    from app.models.lead import Lead
    from app.models.opportunity import Opportunity
    from app.models.organization import Organization
    from app.models.activity import Activity

class Company(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """
    Represents a CRM company inside an organization.

    Every company belongs to exactly one organization.
    """

    __tablename__ = "companies"

    __table_args__ = (
        Index(
            "ix_companies_organization_email",
            "organization_id",
            "email",
        ),
        Index(
            "ix_companies_organization_name",
            "organization_id",
            "name",
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

    contacts: Mapped[list["Contact"]] = relationship(
        "Contact",
        back_populates="company",
        passive_deletes=True,
        lazy="raise",
    )

    leads: Mapped[list["Lead"]] = relationship(
        "Lead",
        back_populates="company",
        passive_deletes=True,
        lazy="raise",
    )

    opportunities: Mapped[list["Opportunity"]] = relationship(
        "Opportunity",
        back_populates="company",
        passive_deletes=True,
        lazy="raise",
    )
    
    
    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        back_populates="company",
        passive_deletes=True,
        lazy="raise",
    )
    
    

__all__ = [
    "Company",
]