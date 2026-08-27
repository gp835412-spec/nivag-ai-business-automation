"""
==========================================================
NIVAG AI Business Automation

Opportunity Response Schema

Response schema for tenant-scoped CRM opportunities.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.opportunity import OpportunityStage


class OpportunityResponse(BaseModel):
    """
    Response schema representing a CRM opportunity.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    organization_id: UUID

    lead_id: UUID | None

    company_id: UUID | None

    contact_id: UUID | None

    name: str

    stage: OpportunityStage

    amount: Decimal | None

    currency: str

    description: str | None

    created_at: datetime

    updated_at: datetime


__all__ = [
    "OpportunityResponse",
]