"""
==========================================================
NIVAG AI Business Automation

Lead Automation Handlers

Stateless automation handlers for CRM lead events.

Responsibilities:
- React to lead lifecycle events.
- Create follow-up activities for newly created leads.
- Acquire a fresh database session per handler execution.
- Preserve organization/tenant isolation.
- Delegate business validation and persistence to
  ActivityService.

The handler intentionally does not retain a request-scoped
database session or ActivityService instance.

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
from app.db.session.database import AsyncSessionLocal
from app.models.activity import (
    ActivityStatus,
    ActivityType,
)
from app.repositories.activity_repository import ActivityRepository
from app.schemas.activity.create import ActivityCreate
from app.services.activity_service import ActivityService


class LeadCreatedActivityHandler:
    """
    Create a follow-up activity when a lead is created.

    The handler is intentionally stateless.

    A fresh AsyncSession is created for every event execution,
    preventing request-bound database sessions from being
    retained by the application-level automation dispatcher.
    """

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

        async with AsyncSessionLocal() as session:
            activity_service = ActivityService(
                repository=ActivityRepository(session),
            )

            await activity_service.create_activity(
                organization_id=event.organization_id,
                data=activity_data,
            )

        


__all__ = [
    "LeadCreatedActivityHandler",
]