"""
==========================================================
NIVAG AI Business Automation

Opportunity Automation Handlers

Handlers for CRM opportunity lifecycle events.

Responsibilities:
- React to OPPORTUNITY_CREATED events.
- Create the initial opportunity follow-up activity.
- Use the application-provided ActivityService.
- Preserve the caller's database transaction.
- Preserve organization/tenant isolation.

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
from app.schemas.activity.create import ActivityCreate
from app.services.activity_service import ActivityService
from app.models.activity import (
    ActivityStatus,
    ActivityType,
)


class OpportunityCreatedActivityHandler:
    """
    Create the initial follow-up activity for a newly created
    CRM opportunity.

    Activity persistence is delegated to the application-provided
    ActivityService so that the handler participates in the same
    database transaction as the originating opportunity operation.
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
        Handle an opportunity-created automation event.

        Only OPPORTUNITY_CREATED events are accepted.
        """

        if event.event_type is not AutomationEventType.OPPORTUNITY_CREATED:
            return

        name = event.payload.get("name")

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                "Opportunity created event requires a non-empty name."
            )

        opportunity_name = name.strip()

        activity_data = ActivityCreate(
            company_id=event.payload.get("company_id"),
            contact_id=event.payload.get("contact_id"),
            lead_id=event.payload.get("lead_id"),
            opportunity_id=event.entity_id,
            activity_type=ActivityType.TASK,
            status=ActivityStatus.PENDING,
            subject=f"Follow up on {opportunity_name}",
            description=(
                "Follow up regarding the opportunity "
                f"'{opportunity_name}'."
            ),
            due_at=None,
            completed_at=None,
        )

        await self._activity_service.create_activity(
            organization_id=event.organization_id,
            data=activity_data,
        )


__all__ = [
    "OpportunityCreatedActivityHandler",
]