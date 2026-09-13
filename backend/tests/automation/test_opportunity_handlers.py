"""
Tests for Opportunity automation handlers.
"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.automation.events import (
    AutomationEvent,
    AutomationEventType,
)
from app.automation.opportunity_handlers import (
    OpportunityCreatedActivityHandler,
)
from app.models.activity import (
    ActivityStatus,
    ActivityType,
)
from app.services.activity_service import ActivityService


@pytest.mark.asyncio
async def test_opportunity_created_handler_creates_follow_up_activity():
    organization_id = uuid4()
    opportunity_id = uuid4()
    company_id = uuid4()
    contact_id = uuid4()
    lead_id = uuid4()

    event = AutomationEvent(
        event_type=AutomationEventType.OPPORTUNITY_CREATED,
        organization_id=organization_id,
        entity_id=opportunity_id,
        occurred_at=Mock(),
        payload={
            "name": "Enterprise CRM Implementation",
            "stage": "qualification",
            "amount": 250000,
            "currency": "INR",
            "company_id": company_id,
            "contact_id": contact_id,
            "lead_id": lead_id,
        },
    )

    create_activity = AsyncMock()

    activity_service = Mock(spec=ActivityService)
    activity_service.create_activity = create_activity

    handler = OpportunityCreatedActivityHandler(
        activity_service=activity_service,
    )

    await handler(event)

    create_activity.assert_awaited_once()

    call = create_activity.await_args

    assert call.kwargs["organization_id"] == organization_id

    activity = call.kwargs["data"]

    assert activity.company_id == company_id
    assert activity.contact_id == contact_id
    assert activity.lead_id == lead_id
    assert activity.opportunity_id == opportunity_id
    assert activity.activity_type is ActivityType.TASK
    assert activity.status is ActivityStatus.PENDING
    assert activity.subject == "Follow up on Enterprise CRM Implementation"
    assert activity.completed_at is None


@pytest.mark.asyncio
async def test_opportunity_created_handler_ignores_other_event_types():
    event = AutomationEvent(
        event_type=AutomationEventType.OPPORTUNITY_UPDATED,
        organization_id=uuid4(),
        entity_id=uuid4(),
        occurred_at=Mock(),
        payload={
            "name": "Enterprise CRM Implementation",
        },
    )

    activity_service = Mock(spec=ActivityService)
    activity_service.create_activity = AsyncMock()

    handler = OpportunityCreatedActivityHandler(
        activity_service=activity_service,
    )

    await handler(event)

    activity_service.create_activity.assert_not_awaited()


@pytest.mark.asyncio
async def test_opportunity_created_handler_rejects_missing_name():
    event = AutomationEvent(
        event_type=AutomationEventType.OPPORTUNITY_CREATED,
        organization_id=uuid4(),
        entity_id=uuid4(),
        occurred_at=Mock(),
        payload={},
    )

    activity_service = Mock(spec=ActivityService)
    activity_service.create_activity = AsyncMock()

    handler = OpportunityCreatedActivityHandler(
        activity_service=activity_service,
    )

    with pytest.raises(
        ValueError,
        match="requires a non-empty name",
    ):
        await handler(event)

    activity_service.create_activity.assert_not_awaited()


@pytest.mark.asyncio
async def test_opportunity_created_handler_rejects_blank_name():
    event = AutomationEvent(
        event_type=AutomationEventType.OPPORTUNITY_CREATED,
        organization_id=uuid4(),
        entity_id=uuid4(),
        occurred_at=Mock(),
        payload={
            "name": "   ",
        },
    )

    activity_service = Mock(spec=ActivityService)
    activity_service.create_activity = AsyncMock()

    handler = OpportunityCreatedActivityHandler(
        activity_service=activity_service,
    )

    with pytest.raises(
        ValueError,
        match="requires a non-empty name",
    ):
        await handler(event)

    activity_service.create_activity.assert_not_awaited()