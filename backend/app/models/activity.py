"""
==========================================================
NIVAG AI Business Automation

Activity Model

Tenant-scoped CRM activity entity.

An activity represents a business interaction, task, call,
email, meeting, or note associated with CRM entities.

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
    DateTime,
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
    from app.models.contact import Contact
    from app.models.lead import Lead
    from app.models.opportunity import Opportunity
    from app.models.organization import Organization


class ActivityType(StrEnum):
    """Type of CRM activity."""

    TASK = "task"
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"


class ActivityStatus(StrEnum):
    """Lifecycle status of a CRM activity."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Activity(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """
    Represents a CRM activity inside an organization.

    Every activity belongs to exactly one organization and
    may optionally be associated with a company, contact,
    lead, or opportunity.
    """

    __tablename__ = "activities"

    __table_args__ = (
        Index(
            "ix_activities_organization_type",
            "organization_id",
            "activity_type",
        ),
        Index(
            "ix_activities_organization_status",
            "organization_id",
            "status",
        ),
        Index(
            "ix_activities_organization_company_id",
            "organization_id",
            "company_id",
        ),
        Index(
            "ix_activities_organization_contact_id",
            "organization_id",
            "contact_id",
        ),
        Index(
            "ix_activities_organization_lead_id",
            "organization_id",
            "lead_id",
        ),
        Index(
            "ix_activities_organization_opportunity_id",
            "organization_id",
            "opportunity_id",
        ),
        Index(
            "ix_activities_organization_due_at",
            "organization_id",
            "due_at",
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

    lead_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "leads.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    opportunity_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "opportunities.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    activity_type: Mapped[ActivityType] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    status: Mapped[ActivityStatus] = mapped_column(
        String(32),
        nullable=False,
        default=ActivityStatus.PENDING,
        server_default=ActivityStatus.PENDING.value,
        index=True,
    )

    subject: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    due_at: Mapped[DateTime | None] = mapped_column(
        DateTime(
            timezone=True,
        ),
        nullable=True,
    )

    completed_at: Mapped[DateTime | None] = mapped_column(
        DateTime(
            timezone=True,
        ),
        nullable=True,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="activities",
        lazy="raise",
    )

    company: Mapped["Company | None"] = relationship(
        "Company",
        back_populates="activities",
        lazy="raise",
    )

    contact: Mapped["Contact | None"] = relationship(
        "Contact",
        back_populates="activities",
        lazy="raise",
    )

    lead: Mapped["Lead | None"] = relationship(
        "Lead",
        back_populates="activities",
        lazy="raise",
    )

    opportunity: Mapped["Opportunity | None"] = relationship(
        "Opportunity",
        back_populates="activities",
        lazy="raise",
    )


__all__ = [
    "Activity",
    "ActivityStatus",
    "ActivityType",
]