from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.automation.events import (
    AutomationEvent,
    AutomationEventType,
)


def test_automation_event_type_values() -> None:
    assert AutomationEventType.ACTIVITY_CREATED.value == "activity.created"
    assert AutomationEventType.ACTIVITY_UPDATED.value == "activity.updated"
    assert AutomationEventType.ACTIVITY_COMPLETED.value == "activity.completed"
    assert AutomationEventType.ACTIVITY_DELETED.value == "activity.deleted"
    assert AutomationEventType.COMPANY_CREATED.value == "company.created"
    assert AutomationEventType.COMPANY_UPDATED.value == "company.updated"
    assert AutomationEventType.CONTACT_CREATED.value == "contact.created"
    assert AutomationEventType.CONTACT_UPDATED.value == "contact.updated"
    assert AutomationEventType.LEAD_CREATED.value == "lead.created"
    assert AutomationEventType.LEAD_UPDATED.value == "lead.updated"
    assert AutomationEventType.OPPORTUNITY_CREATED.value == "opportunity.created"
    assert AutomationEventType.OPPORTUNITY_UPDATED.value == "opportunity.updated"


def test_automation_event_creation() -> None:
    organization_id = uuid4()
    entity_id = uuid4()
    occurred_at = datetime.now(timezone.utc)
    payload = {
        "subject": "Follow up with customer",
        "status": "pending",
    }

    event = AutomationEvent(
        event_type=AutomationEventType.ACTIVITY_CREATED,
        organization_id=organization_id,
        entity_id=entity_id,
        occurred_at=occurred_at,
        payload=payload,
    )

    assert event.event_type is AutomationEventType.ACTIVITY_CREATED
    assert event.organization_id == organization_id
    assert event.entity_id == entity_id
    assert event.occurred_at == occurred_at
    assert event.payload == payload


def test_automation_event_is_immutable() -> None:
    event = AutomationEvent(
        event_type=AutomationEventType.ACTIVITY_CREATED,
        organization_id=uuid4(),
        entity_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        payload={},
    )

    with pytest.raises(FrozenInstanceError):
        event.event_type = AutomationEventType.ACTIVITY_UPDATED  # type: ignore[misc]


def test_automation_event_supports_empty_payload() -> None:
    event = AutomationEvent(
        event_type=AutomationEventType.ACTIVITY_DELETED,
        organization_id=uuid4(),
        entity_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        payload={},
    )

    assert event.payload == {}


def test_automation_event_is_slot_based() -> None:
    event = AutomationEvent(
        event_type=AutomationEventType.COMPANY_CREATED,
        organization_id=uuid4(),
        entity_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        payload={},
    )

    assert not hasattr(event, "__dict__")
