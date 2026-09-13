"""
==========================================================
NIVAG AI Business Automation

Automation Workflow Contracts

Defines the framework-neutral contracts used to decide
whether an automation workflow should execute for a domain
event.

Responsibilities:
- Define workflow trigger conditions.
- Define workflow actions.
- Keep workflow definitions immutable.
- Keep workflow matching independent from HTTP and database
  implementations.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import UUID

from app.automation.events import AutomationEventType


class WorkflowActionType(StrEnum):
    """
    Supported automation workflow actions.
    """

    CREATE_ACTIVITY = "create_activity"


@dataclass(frozen=True, slots=True)
class WorkflowTrigger:
    """
    Defines the event that can activate a workflow.
    """

    event_type: AutomationEventType


@dataclass(frozen=True, slots=True)
class WorkflowAction:
    """
    Defines one action executed when a workflow matches.
    """

    action_type: WorkflowActionType
    parameters: dict[str, Any]


@dataclass(frozen=True, slots=True)
class AutomationWorkflow:
    """
    Immutable automation workflow definition.

    A workflow is activated when its trigger matches the
    incoming automation event.
    """

    id: UUID
    organization_id: UUID
    name: str
    enabled: bool
    trigger: WorkflowTrigger
    actions: tuple[WorkflowAction, ...]


__all__ = [
    "AutomationWorkflow",
    "WorkflowAction",
    "WorkflowActionType",
    "WorkflowTrigger",
]