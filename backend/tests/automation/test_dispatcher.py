from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.automation.dispatcher import AutomationDispatcher
from app.automation.events import (
    AutomationEvent,
    AutomationEventType,
)


def make_event(
    event_type: AutomationEventType = AutomationEventType.ACTIVITY_CREATED,
) -> AutomationEvent:
    return AutomationEvent(
        event_type=event_type,
        organization_id=uuid4(),
        entity_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        payload={"subject": "Test activity"},
    )


@pytest.mark.asyncio
async def test_dispatch_calls_registered_handler() -> None:
    dispatcher = AutomationDispatcher()
    received: list[AutomationEvent] = []

    async def handler(event: AutomationEvent) -> None:
        received.append(event)

    dispatcher.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler,
    )

    event = make_event()

    await dispatcher.dispatch(event)

    assert received == [event]


@pytest.mark.asyncio
async def test_dispatch_calls_multiple_handlers_in_order() -> None:
    dispatcher = AutomationDispatcher()
    calls: list[str] = []

    async def first(event: AutomationEvent) -> None:
        calls.append("first")

    async def second(event: AutomationEvent) -> None:
        calls.append("second")

    dispatcher.register(
        AutomationEventType.ACTIVITY_CREATED,
        first,
    )
    dispatcher.register(
        AutomationEventType.ACTIVITY_CREATED,
        second,
    )

    await dispatcher.dispatch(make_event())

    assert calls == ["first", "second"]


@pytest.mark.asyncio
async def test_dispatch_does_not_call_other_event_handlers() -> None:
    dispatcher = AutomationDispatcher()
    calls: list[str] = []

    async def activity_handler(event: AutomationEvent) -> None:
        calls.append("activity")

    async def company_handler(event: AutomationEvent) -> None:
        calls.append("company")

    dispatcher.register(
        AutomationEventType.ACTIVITY_CREATED,
        activity_handler,
    )
    dispatcher.register(
        AutomationEventType.COMPANY_CREATED,
        company_handler,
    )

    await dispatcher.dispatch(
        make_event(AutomationEventType.ACTIVITY_CREATED),
    )

    assert calls == ["activity"]


@pytest.mark.asyncio
async def test_dispatch_without_handlers_succeeds() -> None:
    dispatcher = AutomationDispatcher()

    await dispatcher.dispatch(make_event())


def test_register_does_not_duplicate_handler() -> None:
    dispatcher = AutomationDispatcher()

    async def handler(event: AutomationEvent) -> None:
        return None

    dispatcher.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler,
    )
    dispatcher.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler,
    )

    assert dispatcher.handlers_for(
        AutomationEventType.ACTIVITY_CREATED,
    ) == (handler,)


def test_unregister_removes_handler() -> None:
    dispatcher = AutomationDispatcher()

    async def handler(event: AutomationEvent) -> None:
        return None

    dispatcher.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler,
    )

    dispatcher.unregister(
        AutomationEventType.ACTIVITY_CREATED,
        handler,
    )

    assert dispatcher.handlers_for(
        AutomationEventType.ACTIVITY_CREATED,
    ) == ()

    assert not dispatcher.has_handlers(
        AutomationEventType.ACTIVITY_CREATED,
    )


def test_unregister_unknown_handler_raises_value_error() -> None:
    dispatcher = AutomationDispatcher()

    async def handler(event: AutomationEvent) -> None:
        return None

    with pytest.raises(
        ValueError,
        match="Handler is not registered for this event type.",
    ):
        dispatcher.unregister(
            AutomationEventType.ACTIVITY_CREATED,
            handler,
        )


def test_handlers_for_unregistered_event_returns_empty_tuple() -> None:
    dispatcher = AutomationDispatcher()

    assert dispatcher.handlers_for(
        AutomationEventType.ACTIVITY_CREATED,
    ) == ()

    assert not dispatcher.has_handlers(
        AutomationEventType.ACTIVITY_CREATED,
    )
