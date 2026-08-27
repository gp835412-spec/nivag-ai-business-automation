"""
==========================================================
NIVAG AI Business Automation

Create Activity Schema

Request validation schema for creating a tenant-scoped
CRM activity.

The organization_id is intentionally not accepted from the
client. It is always resolved from the authenticated tenant
context.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.models.activity import (
    ActivityStatus,
    ActivityType,
)


class ActivityCreate(BaseModel):
    """
    Request schema for creating a tenant-scoped CRM activity.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    company_id: UUID | None = None

    contact_id: UUID | None = None

    lead_id: UUID | None = None

    opportunity_id: UUID | None = None

    activity_type: ActivityType

    status: ActivityStatus = ActivityStatus.PENDING

    subject: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    due_at: datetime | None = None

    completed_at: datetime | None = None

    @field_validator("subject")
    @classmethod
    def validate_subject(
        cls,
        value: str,
    ) -> str:
        """
        Ensure the activity subject is not blank.
        """

        if not value:
            raise ValueError(
                "Activity subject must not be blank.",
            )

        return value


__all__ = [
    "ActivityCreate",
]