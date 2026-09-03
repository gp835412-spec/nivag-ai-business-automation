"""
==========================================================
NIVAG AI Business Automation

Automation Events

Domain-level event contracts used by the automation layer.

Responsibilities:
- Define supported automation event types.
- Provide immutable event payloads.
- Keep automation events independent from persistence,
  HTTP routes, and background-worker implementations.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID


class AutomationEventType(StrEnum):
    """Supported CRM automation event types."""

    ACTIVITY_CREATED = "activity.created"
    ACTIVITY_UPDATED = "activity.updated"
    ACTIVITY_COMPLETED = "activity.completed"
    ACTIVITY_DELETED = "activity.deleted"

    COMPANY_CREATED = "company.created"
    COMPANY_UPDATED = "company.updated"

    CONTACT_CREATED = "contact.created"
    CONTACT_UPDATED = "contact.updated"

    LEAD_CREATED = "lead.created"
    LEAD_UPDATED = "lead.updated"
    LEAD_STATUS_CHANGED = "lead.status_changed"

    OPPORTUNITY_CREATED = "opportunity.created"
    OPPORTUNITY_UPDATED = "opportunity.updated"


@dataclass(frozen=True, slots=True)
class AutomationEvent:
    """
    Immutable domain event emitted by the automation layer.

    Attributes:
        event_type:
            Type of automation event.
        organization_id:
            Tenant/organization that owns the event.
        entity_id:
            Identifier of the entity that triggered the event.
        occurred_at:
            UTC timestamp representing when the event occurred.
        payload:
            Additional event-specific data.
    """

    event_type: AutomationEventType
    organization_id: UUID
    entity_id: UUID
    occurred_at: datetime
    payload: dict[str, Any]


__all__ = [
    "AutomationEvent",
    "AutomationEventType",
]