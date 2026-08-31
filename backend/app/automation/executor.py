"""
==========================================================
NIVAG AI Business Automation

Automation Executor

Executes automation event handlers.

Responsibilities:
- Execute registered asynchronous handlers.
- Preserve handler execution order.
- Keep execution independent from HTTP and persistence.
- Propagate handler failures to the caller.

Registration and event routing remain the responsibility
of AutomationHandlerRegistry and AutomationDispatcher.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from app.automation.events import AutomationEvent
from app.automation.handlers import (
    AutomationHandler,
    AutomationHandlerRegistry,
)


class AutomationExecutor:
    """
    Executes handlers registered for automation events.
    """

    def __init__(
        self,
        registry: AutomationHandlerRegistry,
    ) -> None:
        self._registry = registry

    async def execute(
        self,
        event: AutomationEvent,
    ) -> None:
        """
        Execute all handlers registered for the event type.

        Handlers execute sequentially in registration order.

        Any exception raised by a handler is propagated to the
        caller and stops subsequent handler execution.
        """

        handlers = self._registry.get_handlers(
            event.event_type,
        )

        for handler in handlers:
            await self._execute_handler(
                handler,
                event,
            )

    @staticmethod
    async def _execute_handler(
        handler: AutomationHandler,
        event: AutomationEvent,
    ) -> None:
        """
        Execute a single automation handler.
        """

        await handler(event)


__all__ = [
    "AutomationExecutor",
]