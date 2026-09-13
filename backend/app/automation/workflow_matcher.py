"""
==========================================================
NIVAG AI Business Automation

Workflow Matcher

Determines whether an automation workflow is eligible to
run for a given automation event.

Responsibilities:
- Match workflow organization.
- Match workflow enabled state.
- Match workflow trigger event type.
- Keep matching deterministic and side-effect free.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from app.automation.events import AutomationEvent
from app.automation.workflow import AutomationWorkflow


class WorkflowMatcher:
    """
    Matches automation workflows against incoming events.
    """

    @staticmethod
    def matches(
        workflow: AutomationWorkflow,
        event: AutomationEvent,
    ) -> bool:
        """
        Return True when the workflow is eligible for the event.
        """

        if not workflow.enabled:
            return False

        if workflow.organization_id != event.organization_id:
            return False

        if workflow.trigger.event_type != event.event_type:
            return False

        return True


__all__ = [
    "WorkflowMatcher",
]