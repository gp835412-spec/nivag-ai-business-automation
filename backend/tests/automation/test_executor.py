"""
==========================================================
NIVAG AI Business Automation

Automation Executor Tests

Tests execution of registered asynchronous automation
handlers.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.automation.events import (
    AutomationEvent,
    AutomationEventType,
)
from app.automation.executor import AutomationExecutor
from app.automation.handlers import (
    AutomationHandlerRegistry,
)


@pytest.fixture
def event() -> AutomationEvent:
    """
    Return a valid automation event for executor tests.
    """

    return AutomationEvent(
        event_type=AutomationEventType.ACTIVITY_CREATED,
        organization_id=uuid4(),
        entity_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        payload={
            "activity_id": "activity-123",
        },
    )

@pytest.fixture
def registry() -> AutomationHandlerRegistry:
    """
    Return an isolated handler registry.
    """

    return AutomationHandlerRegistry()


@pytest.fixture
def executor(
    registry: AutomationHandlerRegistry,
) -> AutomationExecutor:
    """
    Return an executor configured with the test registry.
    """

    return AutomationExecutor(
        registry=registry,
    )


@pytest.mark.asyncio
async def test_execute_calls_registered_handler(
    executor: AutomationExecutor,
    registry: AutomationHandlerRegistry,
    event: AutomationEvent,
) -> None:
    """
    Execute must call the handler registered for the event.
    """

    handler = AsyncMock()

    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler,
    )

    await executor.execute(event)

    handler.assert_awaited_once_with(event)


@pytest.mark.asyncio
async def test_execute_calls_multiple_handlers_in_registration_order(
    executor: AutomationExecutor,
    registry: AutomationHandlerRegistry,
    event: AutomationEvent,
) -> None:
    """
    Execute must preserve handler registration order.
    """

    execution_order: list[str] = []

    async def first_handler(
        received_event: AutomationEvent,
    ) -> None:
        assert received_event is event
        execution_order.append("first")

    async def second_handler(
        received_event: AutomationEvent,
    ) -> None:
        assert received_event is event
        execution_order.append("second")

    async def third_handler(
        received_event: AutomationEvent,
    ) -> None:
        assert received_event is event
        execution_order.append("third")

    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        first_handler,
    )
    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        second_handler,
    )
    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        third_handler,
    )

    await executor.execute(event)

    assert execution_order == [
        "first",
        "second",
        "third",
    ]


@pytest.mark.asyncio
async def test_execute_does_not_call_handlers_for_other_event_types(
    executor: AutomationExecutor,
    registry: AutomationHandlerRegistry,
    event: AutomationEvent,
) -> None:
    """
    Execute must only execute handlers registered for the
    event's type.
    """

    matching_handler = AsyncMock()
    unrelated_handler = AsyncMock()

    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        matching_handler,
    )
    registry.register(
        AutomationEventType.COMPANY_CREATED,
        unrelated_handler,
    )

    await executor.execute(event)

    matching_handler.assert_awaited_once_with(event)
    unrelated_handler.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_without_handlers_succeeds(
    executor: AutomationExecutor,
    event: AutomationEvent,
) -> None:
    """
    Execute must safely complete when no handlers are registered.
    """

    result = await executor.execute(event)

    assert result is None


@pytest.mark.asyncio
async def test_execute_propagates_handler_exception(
    executor: AutomationExecutor,
    registry: AutomationHandlerRegistry,
    event: AutomationEvent,
) -> None:
    """
    Execute must propagate handler failures to the caller.
    """

    expected_error = RuntimeError(
        "automation handler failed",
    )

    handler = AsyncMock(
        side_effect=expected_error,
    )

    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler,
    )

    with pytest.raises(
        RuntimeError,
        match="automation handler failed",
    ):
        await executor.execute(event)

    handler.assert_awaited_once_with(event)


@pytest.mark.asyncio
async def test_execute_stops_after_handler_failure(
    executor: AutomationExecutor,
    registry: AutomationHandlerRegistry,
    event: AutomationEvent,
) -> None:
    """
    Execute must stop subsequent handler execution when a
    registered handler raises an exception.
    """

    first_handler = AsyncMock(
        side_effect=RuntimeError(
            "first handler failed",
        ),
    )
    second_handler = AsyncMock()

    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        first_handler,
    )
    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        second_handler,
    )

    with pytest.raises(
        RuntimeError,
        match="first handler failed",
    ):
        await executor.execute(event)

    first_handler.assert_awaited_once_with(event)
    second_handler.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_passes_same_event_instance_to_every_handler(
    executor: AutomationExecutor,
    registry: AutomationHandlerRegistry,
    event: AutomationEvent,
) -> None:
    """
    Execute must pass the exact event instance to every
    registered handler.
    """

    received_events: list[AutomationEvent] = []

    async def first_handler(
        received_event: AutomationEvent,
    ) -> None:
        received_events.append(received_event)

    async def second_handler(
        received_event: AutomationEvent,
    ) -> None:
        received_events.append(received_event)

    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        first_handler,
    )
    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        second_handler,
    )

    await executor.execute(event)

    assert received_events == [
        event,
        event,
    ]

    assert received_events[0] is event
    assert received_events[1] is event