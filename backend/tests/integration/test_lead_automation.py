"""
Integration tests for Lead automation.

Verifies that Lead creation and its initial follow-up
Activity are persisted through the same database session
and transaction.
"""

from uuid import uuid4

import pytest
from sqlalchemy import select

from app.automation import (
    AutomationDispatcher,
    AutomationEventType,
)
from app.automation.lead_handlers import (
    LeadCreatedActivityHandler,
)
from app.models.activity import (
    Activity,
    ActivityStatus,
    ActivityType,
)
from app.models.organization import Organization
from app.repositories.activity_repository import ActivityRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.contact_repository import ContactRepository
from app.repositories.lead_repository import LeadRepository
from app.schemas.lead.lead_schema import LeadCreate
from app.services.activity_service import ActivityService
from app.services.lead_service import LeadService


@pytest.mark.asyncio
async def test_lead_creation_creates_follow_up_activity(
    db_session,
):
    organization = Organization(
        name="NIVAG Lead Integration Test",
        slug=f"nivag-lead-integration-{uuid4().hex[:12]}",
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
        AutomationEventType.LEAD_CREATED,
        LeadCreatedActivityHandler(
            activity_service=activity_service,
        ),
    )

    lead_service = LeadService(
        lead_repository=LeadRepository(
            db_session,
        ),
        company_repository=CompanyRepository(
            db_session,
        ),
        contact_repository=ContactRepository(
            db_session,
        ),
        automation_dispatcher=automation_dispatcher,
    )

    lead = await lead_service.create_lead(
    organization_id=organization.id,
    payload=LeadCreate(
            title="Enterprise CRM Requirement",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            source="website",
            estimated_value=250000,
            currency="INR",
            description="Integration test lead.",
        ),
    )

    result = await db_session.execute(
        select(Activity).where(
            Activity.organization_id == organization.id,
            Activity.lead_id == lead.id,
        )
    )

    activity = result.scalar_one()

    assert activity.organization_id == organization.id
    assert activity.lead_id == lead.id
    assert activity.activity_type == ActivityType.TASK
    assert activity.status == ActivityStatus.PENDING
    assert activity.subject == (
        "Follow up on Enterprise CRM Requirement"
    )