"""
==========================================================
NIVAG AI Business Automation

Update Activity Schema

Request validation schema for partially updating a
tenant-scoped CRM activity.

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


class ActivityUpdate(BaseModel):
    """
    Request schema for partially updating a tenant-scoped
    CRM activity.

    All fields are optional. Fields not explicitly supplied
    by the client remain unchanged.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    company_id: UUID | None = None

    contact_id: UUID | None = None

    lead_id: UUID | None = None

    opportunity_id: UUID | None = None

    activity_type: ActivityType | None = None

    status: ActivityStatus | None = None

    subject: str | None = Field(
        default=None,
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
        value: str | None,
    ) -> str | None:
        """
        Ensure a provided activity subject is not blank.
        """

        if value is not None and not value:
            raise ValueError(
                "Activity subject must not be blank.",
            )

        return value


__all__ = [
    "ActivityUpdate",
]