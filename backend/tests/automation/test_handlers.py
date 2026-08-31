"""
==========================================================
NIVAG AI Business Automation

Automation Handler Registry Tests

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
from app.automation.handlers import (
    AutomationHandlerRegistry,
)


async def handler_one(
    event: AutomationEvent,
) -> None:
    return None


async def handler_two(
    event: AutomationEvent,
) -> None:
    return None


def test_register_handler() -> None:
    registry = AutomationHandlerRegistry()

    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler_one,
    )

    assert registry.get_handlers(
        AutomationEventType.ACTIVITY_CREATED,
    ) == (handler_one,)

    assert registry.has_handlers(
        AutomationEventType.ACTIVITY_CREATED,
    )


def test_duplicate_handler_is_not_registered_twice() -> None:
    registry = AutomationHandlerRegistry()

    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler_one,
    )
    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler_one,
    )

    assert registry.get_handlers(
        AutomationEventType.ACTIVITY_CREATED,
    ) == (handler_one,)


def test_multiple_handlers_preserve_registration_order() -> None:
    registry = AutomationHandlerRegistry()

    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler_one,
    )
    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler_two,
    )

    assert registry.get_handlers(
        AutomationEventType.ACTIVITY_CREATED,
    ) == (
        handler_one,
        handler_two,
    )


def test_handlers_are_scoped_by_event_type() -> None:
    registry = AutomationHandlerRegistry()

    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler_one,
    )
    registry.register(
        AutomationEventType.COMPANY_CREATED,
        handler_two,
    )

    assert registry.get_handlers(
        AutomationEventType.ACTIVITY_CREATED,
    ) == (handler_one,)

    assert registry.get_handlers(
        AutomationEventType.COMPANY_CREATED,
    ) == (handler_two,)


def test_unregister_handler() -> None:
    registry = AutomationHandlerRegistry()

    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler_one,
    )

    registry.unregister(
        AutomationEventType.ACTIVITY_CREATED,
        handler_one,
    )

    assert registry.get_handlers(
        AutomationEventType.ACTIVITY_CREATED,
    ) == ()

    assert not registry.has_handlers(
        AutomationEventType.ACTIVITY_CREATED,
    )


def test_unregister_unknown_handler_raises_value_error() -> None:
    registry = AutomationHandlerRegistry()

    try:
        registry.unregister(
            AutomationEventType.ACTIVITY_CREATED,
            handler_one,
        )
    except ValueError as exc:
        assert str(exc) == (
            "Handler is not registered for this event type."
        )
    else:
        raise AssertionError(
            "Expected ValueError was not raised.",
        )


def test_clear_removes_all_handlers_for_event_type() -> None:
    registry = AutomationHandlerRegistry()

    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler_one,
    )
    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler_two,
    )

    registry.clear(
        AutomationEventType.ACTIVITY_CREATED,
    )

    assert registry.get_handlers(
        AutomationEventType.ACTIVITY_CREATED,
    ) == ()

    assert not registry.has_handlers(
        AutomationEventType.ACTIVITY_CREATED,
    )


def test_clear_does_not_affect_other_event_types() -> None:
    registry = AutomationHandlerRegistry()

    registry.register(
        AutomationEventType.ACTIVITY_CREATED,
        handler_one,
    )
    registry.register(
        AutomationEventType.COMPANY_CREATED,
        handler_two,
    )

    registry.clear(
        AutomationEventType.ACTIVITY_CREATED,
    )

    assert not registry.has_handlers(
        AutomationEventType.ACTIVITY_CREATED,
    )

    assert registry.get_handlers(
        AutomationEventType.COMPANY_CREATED,
    ) == (handler_two,)