"""
==========================================================
NIVAG AI Business Automation

Automation Handlers

Handler contracts and registration utilities for the
automation event system.

Responsibilities:
- Define the automation handler contract.
- Provide a reusable handler registry.
- Register handlers by event type.
- Unregister handlers safely.
- Expose registered handlers for dispatcher integration.

Business logic belongs in the concrete handlers or
application services, not in this registry.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Awaitable, Callable

from app.automation.events import (
    AutomationEvent,
    AutomationEventType,
)


AutomationHandler = Callable[
    [AutomationEvent],
    Awaitable[None],
]


class AutomationHandlerRegistry:
    """
    Registry of asynchronous automation handlers.

    Handlers are stored per event type and returned in their
    registration order.
    """

    def __init__(self) -> None:
        self._handlers: dict[
            AutomationEventType,
            list[AutomationHandler],
        ] = defaultdict(list)

    def register(
        self,
        event_type: AutomationEventType,
        handler: AutomationHandler,
    ) -> None:
        """
        Register a handler for an automation event type.

        Duplicate registrations are ignored.
        """

        handlers = self._handlers[event_type]

        if handler not in handlers:
            handlers.append(handler)

    def unregister(
        self,
        event_type: AutomationEventType,
        handler: AutomationHandler,
    ) -> None:
        """
        Unregister a handler.

        Raises:
            ValueError:
                If the handler is not registered.
        """

        handlers = self._handlers.get(event_type)

        if not handlers or handler not in handlers:
            raise ValueError(
                "Handler is not registered for this event type.",
            )

        handlers.remove(handler)

        if not handlers:
            del self._handlers[event_type]

    def get_handlers(
        self,
        event_type: AutomationEventType,
    ) -> tuple[AutomationHandler, ...]:
        """
        Return handlers registered for an event type.
        """

        return tuple(
            self._handlers.get(
                event_type,
                (),
            ),
        )

    def has_handlers(
        self,
        event_type: AutomationEventType,
    ) -> bool:
        """
        Return whether an event type has registered handlers.
        """

        return bool(
            self._handlers.get(event_type),
        )

    def clear(
        self,
        event_type: AutomationEventType,
    ) -> None:
        """
        Remove all handlers registered for an event type.
        """

        self._handlers.pop(
            event_type,
            None,
        )


__all__ = [
    "AutomationHandler",
    "AutomationHandlerRegistry",
]