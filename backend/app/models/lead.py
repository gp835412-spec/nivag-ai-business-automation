"""
==========================================================
NIVAG AI Business Automation

Lead Model

Tenant-scoped CRM lead entity.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    Index,
    Numeric,
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
    from app.models.activity import Activity
    from app.models.company import Company
    from app.models.contact import Contact
    from app.models.opportunity import Opportunity
    from app.models.organization import Organization


class LeadStatus(StrEnum):
    """Lifecycle status of a CRM lead."""

    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class Lead(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """
    Represents a potential business opportunity inside
    an organization.
    """

    __tablename__ = "leads"

    __table_args__ = (
        Index(
            "ix_leads_organization_status",
            "organization_id",
            "status",
        ),
        Index(
            "ix_leads_organization_company_id",
            "organization_id",
            "company_id",
        ),
        Index(
            "ix_leads_organization_contact_id",
            "organization_id",
            "contact_id",
        ),
        Index(
            "ix_leads_organization_title",
            "organization_id",
            "title",
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

    contact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "contacts.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    first_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
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

    company_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[LeadStatus] = mapped_column(
        String(32),
        nullable=False,
        default=LeadStatus.NEW,
        server_default=LeadStatus.NEW.value,
        index=True,
    )

    estimated_value: Mapped[float | None] = mapped_column(
        Numeric(
            precision=18,
            scale=2,
        ),
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR",
        server_default="INR",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="leads",
        lazy="raise",
    )

    company: Mapped["Company | None"] = relationship(
        "Company",
        back_populates="leads",
        lazy="raise",
    )

    contact: Mapped["Contact | None"] = relationship(
        "Contact",
        back_populates="leads",
        lazy="raise",
    )

    opportunities: Mapped[list["Opportunity"]] = relationship(
        "Opportunity",
        back_populates="lead",
        passive_deletes=True,
        lazy="raise",
    )

    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        back_populates="lead",
        passive_deletes=True,
        lazy="raise",
    )


__all__ = [
    "Lead",
    "LeadStatus",
]