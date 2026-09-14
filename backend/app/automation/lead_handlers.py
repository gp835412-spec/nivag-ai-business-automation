"""
==========================================================
NIVAG AI Business Automation

Lead Automation Handlers

Automation handlers for CRM lead events.

Responsibilities:
- React to lead lifecycle events.
- Create follow-up activities for newly created leads.
- Use the request-scoped ActivityService.
- Preserve organization/tenant isolation.
- Delegate business validation and persistence to
  ActivityService.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from app.automation.events import (
    AutomationEvent,
    AutomationEventType,
)
from app.models.activity import (
    ActivityStatus,
    ActivityType,
)
from app.schemas.activity.create import ActivityCreate
from app.services.activity_service import ActivityService


class LeadCreatedActivityHandler:
    """
    Create a follow-up activity when a lead is created.

    The ActivityService is injected so the handler participates
    in the same database session and transaction as the lead
    creation operation.
    """

    def __init__(
        self,
        activity_service: ActivityService,
    ) -> None:
        self._activity_service = activity_service

    async def __call__(
        self,
        event: AutomationEvent,
    ) -> None:
        """
        Handle a lead-created automation event.

        Only LEAD_CREATED events are accepted.
        """

        if event.event_type is not AutomationEventType.LEAD_CREATED:
            return

        title = event.payload.get("title")

        if not isinstance(title, str) or not title.strip():
            raise ValueError(
                "Lead created event requires a non-empty title."
            )

        normalized_title = title.strip()

        activity_data = ActivityCreate(
            company_id=None,
            contact_id=None,
            lead_id=event.entity_id,
            opportunity_id=None,
            activity_type=ActivityType.TASK,
            status=ActivityStatus.PENDING,
            subject=f"Follow up on {normalized_title}",
            description=(
                "Follow up with the lead regarding "
                f"the requirement: {normalized_title}."
            ),
            due_at=None,
            completed_at=None,
        )

        await self._activity_service.create_activity(
            organization_id=event.organization_id,
            data=activity_data,
        )


__all__ = [
    "LeadCreatedActivityHandler",
]