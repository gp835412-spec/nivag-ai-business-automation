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
    automation_dispatcher,
)
from app.automation.events import (
    AutomationEvent,
    AutomationEventType,
)
from app.automation.handlers import (
    AutomationHandler,
    AutomationHandlerRegistry,
)

from app.automation.executor import AutomationExecutor

__all__ = [
    "AutomationDispatcher",
    "AutomationEvent",
    "AutomationEventHandler",
    "AutomationEventType",
    "AutomationHandler",
    "AutomationHandlerRegistry",
    "AutomationExecutor",
    "automation_dispatcher",
]