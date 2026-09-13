"""
Integration tests for Opportunity automation.

Verifies that Opportunity creation and its initial follow-up
Activity are persisted through the same database session and
transaction.
"""

from uuid import uuid4

import pytest
from sqlalchemy import select

from app.automation import (
    AutomationDispatcher,
    AutomationEventType,
    OpportunityCreatedActivityHandler,
)
from app.models.activity import Activity, ActivityStatus, ActivityType
from app.models.organization import Organization
from app.repositories.activity_repository import ActivityRepository
from app.repositories.opportunity_repository import OpportunityRepository
from app.schemas.opportunity.create import OpportunityCreate
from app.services.activity_service import ActivityService
from app.services.opportunity_service import OpportunityService


@pytest.mark.asyncio
async def test_opportunity_creation_creates_follow_up_activity(
    db_session,
):
    organization = Organization(
        name="NIVAG Integration Test",
        slug=f"nivag-integration-{uuid4().hex[:12]}",
        timezone="Asia/Kolkata",
        currency="INR",
    )

    db_session.add(organization)
    await db_session.flush()

    activity_service = ActivityService(
        repository=ActivityRepository(
            db_session,
        ),
    )

    automation_dispatcher = AutomationDispatcher()

    automation_dispatcher.register(
        AutomationEventType.OPPORTUNITY_CREATED,
        OpportunityCreatedActivityHandler(
            activity_service=activity_service,
        ),
    )

    opportunity_service = OpportunityService(
        repository=OpportunityRepository(
            db_session,
        ),
        automation_dispatcher=automation_dispatcher,
    )

    opportunity = await opportunity_service.create_opportunity(
        organization_id=organization.id,
        data=OpportunityCreate(
            name="Enterprise CRM Implementation",
            stage="qualification",
            amount=250000,
            currency="INR",
            description="Integration test opportunity.",
        ),
    )

    result = await db_session.execute(
        select(Activity).where(
            Activity.organization_id == organization.id,
            Activity.opportunity_id == opportunity.id,
        )
    )

    activity = result.scalar_one()

    assert activity.organization_id == organization.id
    assert activity.opportunity_id == opportunity.id
    assert activity.activity_type == ActivityType.TASK
    assert activity.status == ActivityStatus.PENDING
    assert activity.subject == (
        "Follow up on Enterprise CRM Implementation"
    )