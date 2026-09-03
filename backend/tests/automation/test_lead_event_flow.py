from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest

from app.automation import (
    AutomationDispatcher,
    AutomationEvent,
    AutomationEventType,
)


@pytest.mark.asyncio
async def test_lead_created_event_reaches_registered_handler() -> None:
    dispatcher = AutomationDispatcher()
    handler = AsyncMock()

    dispatcher.register(
        AutomationEventType.LEAD_CREATED,
        handler,
    )

    event = AutomationEvent(
        event_type=AutomationEventType.LEAD_CREATED,
        organization_id=uuid4(),
        entity_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        payload={
            "lead_id": "lead-001",
            "organization_id": "org-001",
            "title": "AI Business Automation Requirement",
            "status": "new",
        },
    )

    await dispatcher.dispatch(event)

    handler.assert_awaited_once_with(event)


@pytest.mark.asyncio
async def test_lead_updated_event_reaches_registered_handler() -> None:
    dispatcher = AutomationDispatcher()
    handler = AsyncMock()

    dispatcher.register(
        AutomationEventType.LEAD_UPDATED,
        handler,
    )

    event = AutomationEvent(
        event_type=AutomationEventType.LEAD_UPDATED,
        organization_id=uuid4(),
        entity_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        payload={
            "lead_id": "lead-001",
            "organization_id": "org-001",
            "title": "Updated Requirement",
            "status": "qualified",
        },
    )

    await dispatcher.dispatch(event)

    handler.assert_awaited_once_with(event)


@pytest.mark.asyncio
async def test_lead_status_changed_event_reaches_registered_handler() -> None:
    dispatcher = AutomationDispatcher()
    handler = AsyncMock()

    dispatcher.register(
        AutomationEventType.LEAD_STATUS_CHANGED,
        handler,
    )

    event = AutomationEvent(
        event_type=AutomationEventType.LEAD_STATUS_CHANGED,
        organization_id=uuid4(),
        entity_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        payload={
            "lead_id": "lead-001",
            "organization_id": "org-001",
            "previous_status": "new",
            "new_status": "qualified",
        },
    )

    await dispatcher.dispatch(event)

    handler.assert_awaited_once_with(event)


@pytest.mark.asyncio
async def test_lead_handler_receives_exact_event_payload() -> None:
    dispatcher = AutomationDispatcher()
    handler = AsyncMock()

    dispatcher.register(
        AutomationEventType.LEAD_CREATED,
        handler,
    )

    event = AutomationEvent(
        event_type=AutomationEventType.LEAD_CREATED,
        organization_id=uuid4(),
        entity_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        payload={
            "lead_id": "lead-001",
            "organization_id": "org-001",
            "title": "AI Business Automation Requirement",
            "status": "new",
        },
    )

    await dispatcher.dispatch(event)

    received_event = handler.await_args.args[0]

    assert received_event is event
    assert received_event.event_type is AutomationEventType.LEAD_CREATED
    assert received_event.payload["lead_id"] == "lead-001"
    assert received_event.payload["status"] == "new"