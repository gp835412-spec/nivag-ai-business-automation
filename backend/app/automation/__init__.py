"""
==========================================================
NIVAG AI Business Automation

Automation Package

Public exports for the automation domain layer.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from app.automation.dispatcher import (
    AutomationDispatcher,
    AutomationEventHandler,
)
from app.automation.events import (
    AutomationEvent,
    AutomationEventType,
)
from app.automation.handlers import (
    AutomationHandler,
    AutomationHandlerRegistry,
)


__all__ = [
    "AutomationDispatcher",
    "AutomationEvent",
    "AutomationEventHandler",
    "AutomationEventType",
    "AutomationHandler",
    "AutomationHandlerRegistry",
]