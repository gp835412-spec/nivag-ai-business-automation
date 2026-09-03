"""
==========================================================
NIVAG AI Business Automation

Automation Handler Registry Tests

Tests:
- Handler registration.
- Duplicate registration protection.
- Handler retrieval order.
- Handler existence checks.
- Handler unregistration.
- Invalid unregistration.
- Event-type isolation.
- Clearing handlers.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.automation.events import AutomationEventType
from app.automation.handlers import (
    AutomationHandlerRegistry,
)


@pytest.fixture
def registry() -> AutomationHandlerRegistry:
    """Return a fresh handler registry."""
    return AutomationHandlerRegistry()


@pytest.fixture
def handler() -> AsyncMock:
    """Return an asynchronous automation handler."""
    return AsyncMock()


def test_register_handler(
    registry: AutomationHandlerRegistry,
    handler: AsyncMock,
) -> None:
    """A handler can be registered for an event type."""

    registry.register(
        AutomationEventType.LEAD_CREATED,
        handler,
    )

    assert registry.has_handlers(
        AutomationEventType.LEAD_CREATED,
    )

    assert registry.get_handlers(
        AutomationEventType.LEAD_CREATED,
    ) == (handler,)


def test_duplicate_registration_is_ignored(
    registry: AutomationHandlerRegistry,
    handler: AsyncMock,
) -> None:
    """Registering the same handler twice stores it only once."""

    registry.register(
        AutomationEventType.LEAD_CREATED,
        handler,
    )
    registry.register(
        AutomationEventType.LEAD_CREATED,
        handler,
    )

    handlers = registry.get_handlers(
        AutomationEventType.LEAD_CREATED,
    )

    assert handlers == (handler,)


def test_handlers_preserve_registration_order(
    registry: AutomationHandlerRegistry,
) -> None:
    """Handlers are returned in registration order."""

    first_handler = AsyncMock()
    second_handler = AsyncMock()
    third_handler = AsyncMock()

    registry.register(
        AutomationEventType.LEAD_CREATED,
        first_handler,
    )
    registry.register(
        AutomationEventType.LEAD_CREATED,
        second_handler,
    )
    registry.register(
        AutomationEventType.LEAD_CREATED,
        third_handler,
    )

    assert registry.get_handlers(
        AutomationEventType.LEAD_CREATED,
    ) == (
        first_handler,
        second_handler,
        third_handler,
    )


def test_get_handlers_returns_empty_tuple_when_unregistered(
    registry: AutomationHandlerRegistry,
) -> None:
    """An event type without handlers returns an empty tuple."""

    assert registry.get_handlers(
        AutomationEventType.LEAD_CREATED,
    ) == ()


def test_has_handlers_returns_false_when_unregistered(
    registry: AutomationHandlerRegistry,
) -> None:
    """An event type without handlers reports no handlers."""

    assert not registry.has_handlers(
        AutomationEventType.LEAD_CREATED,
    )


def test_handlers_are_isolated_by_event_type(
    registry: AutomationHandlerRegistry,
) -> None:
    """Handlers registered for one event do not affect another."""

    lead_handler = AsyncMock()
    contact_handler = AsyncMock()

    registry.register(
        AutomationEventType.LEAD_CREATED,
        lead_handler,
    )
    registry.register(
        AutomationEventType.CONTACT_CREATED,
        contact_handler,
    )

    assert registry.get_handlers(
        AutomationEventType.LEAD_CREATED,
    ) == (lead_handler,)

    assert registry.get_handlers(
        AutomationEventType.CONTACT_CREATED,
    ) == (contact_handler,)


def test_unregister_handler(
    registry: AutomationHandlerRegistry,
    handler: AsyncMock,
) -> None:
    """A registered handler can be safely removed."""

    registry.register(
        AutomationEventType.LEAD_CREATED,
        handler,
    )

    registry.unregister(
        AutomationEventType.LEAD_CREATED,
        handler,
    )

    assert not registry.has_handlers(
        AutomationEventType.LEAD_CREATED,
    )

    assert registry.get_handlers(
        AutomationEventType.LEAD_CREATED,
    ) == ()


def test_unregister_last_handler_removes_event_type(
    registry: AutomationHandlerRegistry,
) -> None:
    """Removing the final handler removes the event registry entry."""

    handler = AsyncMock()

    registry.register(
        AutomationEventType.LEAD_CREATED,
        handler,
    )

    registry.unregister(
        AutomationEventType.LEAD_CREATED,
        handler,
    )

    assert not registry.has_handlers(
        AutomationEventType.LEAD_CREATED,
    )


def test_unregister_unregistered_handler_raises_value_error(
    registry: AutomationHandlerRegistry,
    handler: AsyncMock,
) -> None:
    """Unregistering a missing handler raises ValueError."""

    with pytest.raises(
        ValueError,
        match="Handler is not registered for this event type.",
    ):
        registry.unregister(
            AutomationEventType.LEAD_CREATED,
            handler,
        )


def test_unregister_from_wrong_event_type_raises_value_error(
    registry: AutomationHandlerRegistry,
    handler: AsyncMock,
) -> None:
    """A handler cannot be removed from an unrelated event type."""

    registry.register(
        AutomationEventType.LEAD_CREATED,
        handler,
    )

    with pytest.raises(
        ValueError,
        match="Handler is not registered for this event type.",
    ):
        registry.unregister(
            AutomationEventType.CONTACT_CREATED,
            handler,
        )

    assert registry.get_handlers(
        AutomationEventType.LEAD_CREATED,
    ) == (handler,)


def test_clear_event_handlers(
    registry: AutomationHandlerRegistry,
) -> None:
    """Clear removes every handler for the selected event type."""

    first_handler = AsyncMock()
    second_handler = AsyncMock()

    registry.register(
        AutomationEventType.LEAD_CREATED,
        first_handler,
    )
    registry.register(
        AutomationEventType.LEAD_CREATED,
        second_handler,
    )

    registry.clear(
        AutomationEventType.LEAD_CREATED,
    )

    assert registry.get_handlers(
        AutomationEventType.LEAD_CREATED,
    ) == ()

    assert not registry.has_handlers(
        AutomationEventType.LEAD_CREATED,
    )


def test_clear_unregistered_event_type_is_safe(
    registry: AutomationHandlerRegistry,
) -> None:
    """Clearing an event type without handlers is a no-op."""

    registry.clear(
        AutomationEventType.LEAD_CREATED,
    )

    assert registry.get_handlers(
        AutomationEventType.LEAD_CREATED,
    ) == ()


def test_clear_does_not_affect_other_event_types(
    registry: AutomationHandlerRegistry,
) -> None:
    """Clearing one event type preserves handlers for other types."""

    lead_handler = AsyncMock()
    contact_handler = AsyncMock()

    registry.register(
        AutomationEventType.LEAD_CREATED,
        lead_handler,
    )
    registry.register(
        AutomationEventType.CONTACT_CREATED,
        contact_handler,
    )

    registry.clear(
        AutomationEventType.LEAD_CREATED,
    )

    assert registry.get_handlers(
        AutomationEventType.LEAD_CREATED,
    ) == ()

    assert registry.get_handlers(
        AutomationEventType.CONTACT_CREATED,
    ) == (contact_handler,)