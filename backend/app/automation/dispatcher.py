"""
==========================================================
NIVAG AI Business Automation

Automation Dispatcher

Dispatches domain automation events to registered
asynchronous handlers.

Responsibilities:
- Route events by event type.
- Delegate handler registration to the handler registry.
- Dispatch handlers sequentially.
- Preserve handler execution order.
- Keep dispatching independent from HTTP and persistence.

The dispatcher owns event routing only. Handler registration
state is owned by AutomationHandlerRegistry.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from app.automation.events import (
    AutomationEvent,
    AutomationEventType,
)
from app.automation.handlers import (
    AutomationHandler,
    AutomationHandlerRegistry,
)


AutomationEventHandler = Callable[
    [AutomationEvent],
    Awaitable[None],
]


class AutomationDispatcher:
    """
    In-process asynchronous dispatcher for automation events.

    Handler registration is delegated to a single
    AutomationHandlerRegistry instance so that the application
    has one authoritative handler registry.
    """

    def __init__(
        self,
        registry: AutomationHandlerRegistry | None = None,
    ) -> None:
        self._registry = (
            registry
            if registry is not None
            else AutomationHandlerRegistry()
        )

    @property
    def registry(self) -> AutomationHandlerRegistry:
        """
        Return the handler registry used by this dispatcher.
        """

        return self._registry

    def register(
        self,
        event_type: AutomationEventType,
        handler: AutomationEventHandler,
    ) -> None:
        """
        Register an asynchronous handler for an event type.
        """

        self._registry.register(
            event_type,
            handler,
        )

    def unregister(
        self,
        event_type: AutomationEventType,
        handler: AutomationEventHandler,
    ) -> None:
        """
        Remove a previously registered handler.
        """

        self._registry.unregister(
            event_type,
            handler,
        )

    async def dispatch(
        self,
        event: AutomationEvent,
    ) -> None:
        """
        Dispatch an event to all registered handlers.

        Handlers execute sequentially in registration order.

        A handler exception is intentionally propagated to the
        caller. Silent failure would make automation execution
        unreliable and would prevent the application or future
        worker layer from applying its own retry/error policy.
        """

        handlers = self._registry.get_handlers(
            event.event_type,
        )

        for handler in handlers:
            await handler(event)

    def handlers_for(
        self,
        event_type: AutomationEventType,
    ) -> tuple[AutomationHandler, ...]:
        """
        Return the handlers currently registered for an event type.
        """

        return self._registry.get_handlers(
            event_type,
        )

    def has_handlers(
        self,
        event_type: AutomationEventType,
    ) -> bool:
        """
        Return whether an event type has registered handlers.
        """

        return self._registry.has_handlers(
            event_type,
        )


__all__ = [
    "AutomationEventHandler",
    "AutomationDispatcher",
]