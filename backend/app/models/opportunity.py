"""
==========================================================
NIVAG AI Business Automation

Opportunity Model

Tenant-scoped CRM opportunity entity.

An opportunity belongs to an organization and may optionally
be associated with an existing lead, company, or contact.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from decimal import Decimal
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
    from app.models.company import Company
    from app.models.contact import Contact
    from app.models.lead import Lead
    from app.models.organization import Organization


class OpportunityStage(StrEnum):
    """Lifecycle stage of a CRM opportunity."""

    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class Opportunity(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """
    Represents a potential revenue opportunity inside
    an organization.

    Every opportunity belongs to exactly one organization.

    It may optionally be associated with a lead, company,
    and/or contact belonging to the same organization.
    """

    __tablename__ = "opportunities"

    __table_args__ = (
        Index(
            "ix_opportunities_organization_stage",
            "organization_id",
            "stage",
        ),
        Index(
            "ix_opportunities_organization_company_id",
            "organization_id",
            "company_id",
        ),
        Index(
            "ix_opportunities_organization_contact_id",
            "organization_id",
            "contact_id",
        ),
        Index(
            "ix_opportunities_organization_lead_id",
            "organization_id",
            "lead_id",
        ),
        Index(
            "ix_opportunities_organization_name",
            "organization_id",
            "name",
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

    lead_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "leads.id",
            ondelete="SET NULL",
        ),
        nullable=True,
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

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    stage: Mapped[OpportunityStage] = mapped_column(
        String(32),
        nullable=False,
        default=OpportunityStage.PROSPECTING,
        server_default=OpportunityStage.PROSPECTING.value,
        index=True,
    )

    amount: Mapped[Decimal | None] = mapped_column(
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
        back_populates="opportunities",
        lazy="raise",
    )

    lead: Mapped["Lead | None"] = relationship(
        "Lead",
        back_populates="opportunities",
        lazy="raise",
    )

    company: Mapped["Company | None"] = relationship(
        "Company",
        back_populates="opportunities",
        lazy="raise",
    )

    contact: Mapped["Contact | None"] = relationship(
        "Contact",
        back_populates="opportunities",
        lazy="raise",
    )


__all__ = [
    "Opportunity",
    "OpportunityStage",
]