"""
==========================================================
NIVAG AI Business Automation

Automation Dispatcher

Dispatches domain automation events to registered
asynchronous handlers.

Responsibilities:
- Register event handlers.
- Dispatch events to matching handlers.
- Support multiple handlers per event type.
- Preserve handler execution order.
- Keep dispatching independent from HTTP and persistence.

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


AutomationEventHandler = Callable[
    [AutomationEvent],
    Awaitable[None],
]


class AutomationDispatcher:
    """
    In-process asynchronous dispatcher for automation events.

    Handlers are registered against a specific
    AutomationEventType and are executed in registration order.
    """

    def __init__(self) -> None:
        self._handlers: dict[
            AutomationEventType,
            list[AutomationEventHandler],
        ] = defaultdict(list)

    def register(
        self,
        event_type: AutomationEventType,
        handler: AutomationEventHandler,
    ) -> None:
        """
        Register an asynchronous handler for an event type.
        """

        if handler in self._handlers[event_type]:
            return

        self._handlers[event_type].append(handler)

    def unregister(
        self,
        event_type: AutomationEventType,
        handler: AutomationEventHandler,
    ) -> None:
        """
        Remove a previously registered handler.

        Raises:
            ValueError:
                If the handler is not registered for the event.
        """

        handlers = self._handlers.get(event_type)

        if not handlers or handler not in handlers:
            raise ValueError(
                "Handler is not registered for this event type.",
            )

        handlers.remove(handler)

        if not handlers:
            del self._handlers[event_type]

    async def dispatch(
        self,
        event: AutomationEvent,
    ) -> None:
        """
        Dispatch an event to all registered handlers.

        Handlers execute sequentially in registration order.
        """

        handlers = tuple(
            self._handlers.get(
                event.event_type,
                (),
            ),
        )

        for handler in handlers:
            await handler(event)

    def handlers_for(
        self,
        event_type: AutomationEventType,
    ) -> tuple[AutomationEventHandler, ...]:
        """
        Return the currently registered handlers for an event type.
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
            self._handlers.get(
                event_type,
            ),
        )


__all__ = [
    "AutomationEventHandler",
    "AutomationDispatcher",
]