"""
==========================================================
NIVAG AI Business Automation

Activity Response Schema

Response schemas for tenant-scoped CRM activity APIs.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.activity import (
    ActivityStatus,
    ActivityType,
)


class ActivityResponse(BaseModel):
    """
    API response schema for a CRM activity.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    organization_id: UUID

    company_id: UUID | None
    contact_id: UUID | None
    lead_id: UUID | None
    opportunity_id: UUID | None

    activity_type: ActivityType
    status: ActivityStatus

    subject: str
    description: str | None

    due_at: datetime | None
    completed_at: datetime | None

    created_at: datetime
    updated_at: datetime


class ActivityListResponse(BaseModel):
    """
    Paginated response schema for CRM activities.
    """

    items: list[ActivityResponse]

    offset: int
    limit: int
    count: int


__all__ = [
    "ActivityListResponse",
    "ActivityResponse",
]