"""
==========================================================
NIVAG AI Business Automation

Activity Service

Business logic for tenant-scoped CRM activities.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from app.models.activity import (
    Activity,
    ActivityStatus,
)
from app.models.company import Company
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.opportunity import Opportunity
from app.repositories.activity_repository import ActivityRepository
from app.schemas.activity.create import ActivityCreate
from app.schemas.activity.update import ActivityUpdate


class ActivityNotFoundError(LookupError):
    """Raised when an activity cannot be found."""


class ActivityValidationError(ValueError):
    """Raised when activity data or references are invalid."""


class ActivityService:
    """
    Application service for tenant-scoped CRM activity
    operations.

    All activity operations are scoped to a single
    organization.

    Related company, contact, lead, and opportunity
    references must belong to the same organization.
    """

    def __init__(
        self,
        repository: ActivityRepository,
    ) -> None:
        self._repository = repository

    async def create_activity(
        self,
        *,
        organization_id: UUID,
        data: ActivityCreate,
    ) -> Activity:
        """
        Create a new CRM activity inside an organization.
        """

        await self._validate_references(
            organization_id=organization_id,
            company_id=data.company_id,
            contact_id=data.contact_id,
            lead_id=data.lead_id,
            opportunity_id=data.opportunity_id,
        )

        self._validate_activity_dates(
            status=data.status,
            due_at=data.due_at,
            completed_at=data.completed_at,
        )

        activity = Activity(
            organization_id=organization_id,
            company_id=data.company_id,
            contact_id=data.contact_id,
            lead_id=data.lead_id,
            opportunity_id=data.opportunity_id,
            activity_type=data.activity_type,
            status=data.status,
            subject=data.subject,
            description=data.description,
            due_at=data.due_at,
            completed_at=data.completed_at,
        )

        return await self._repository.create(
            activity=activity,
        )

    async def get_activity(
        self,
        *,
        organization_id: UUID,
        activity_id: UUID,
    ) -> Activity:
        """
        Return one activity belonging to an organization.
        """

        activity = await self._repository.get_by_id(
            organization_id=organization_id,
            activity_id=activity_id,
        )

        if activity is None:
            raise ActivityNotFoundError(
                "Activity not found.",
            )

        return activity

    async def list_activities(
        self,
        *,
        organization_id: UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Activity]:
        """
        Return activities belonging to an organization.
        """

        return await self._repository.list(
            organization_id=organization_id,
            offset=offset,
            limit=limit,
        )

    async def update_activity(
        self,
        *,
        organization_id: UUID,
        activity_id: UUID,
        data: ActivityUpdate,
    ) -> Activity:
        """
        Update an existing activity.

        Only explicitly supplied fields are modified.
        """

        activity = await self.get_activity(
            organization_id=organization_id,
            activity_id=activity_id,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        company_id = update_data.get(
            "company_id",
            activity.company_id,
        )

        contact_id = update_data.get(
            "contact_id",
            activity.contact_id,
        )

        lead_id = update_data.get(
            "lead_id",
            activity.lead_id,
        )

        opportunity_id = update_data.get(
            "opportunity_id",
            activity.opportunity_id,
        )

        await self._validate_references(
            organization_id=organization_id,
            company_id=company_id,
            contact_id=contact_id,
            lead_id=lead_id,
            opportunity_id=opportunity_id,
        )

        status = update_data.get(
            "status",
            activity.status,
        )

        due_at = update_data.get(
            "due_at",
            activity.due_at,
        )

        completed_at = update_data.get(
            "completed_at",
            activity.completed_at,
        )

        self._validate_activity_dates(
            status=status,
            due_at=due_at,
            completed_at=completed_at,
        )

        for field, value in update_data.items():
            setattr(
                activity,
                field,
                value,
            )

        return await self._repository.update(
            activity=activity,
        )

    async def delete_activity(
        self,
        *,
        organization_id: UUID,
        activity_id: UUID,
    ) -> None:
        """
        Delete an activity belonging to an organization.
        """

        activity = await self.get_activity(
            organization_id=organization_id,
            activity_id=activity_id,
        )

        await self._repository.delete(
            activity=activity,
        )

    async def _validate_references(
        self,
        *,
        organization_id: UUID,
        company_id: UUID | None,
        contact_id: UUID | None,
        lead_id: UUID | None,
        opportunity_id: UUID | None,
    ) -> None:
        """
        Validate that all referenced CRM entities belong to
        the same organization as the activity.
        """

        session = self._repository.session

        if company_id is not None:
            company = await session.get(
                Company,
                company_id,
            )

            if (
                company is None
                or company.organization_id != organization_id
            ):
                raise ActivityValidationError(
                    "Invalid company for this organization.",
                )

        if contact_id is not None:
            contact = await session.get(
                Contact,
                contact_id,
            )

            if (
                contact is None
                or contact.organization_id != organization_id
            ):
                raise ActivityValidationError(
                    "Invalid contact for this organization.",
                )

        if lead_id is not None:
            lead = await session.get(
                Lead,
                lead_id,
            )

            if (
                lead is None
                or lead.organization_id != organization_id
            ):
                raise ActivityValidationError(
                    "Invalid lead for this organization.",
                )

        if opportunity_id is not None:
            opportunity = await session.get(
                Opportunity,
                opportunity_id,
            )

            if (
                opportunity is None
                or opportunity.organization_id != organization_id
            ):
                raise ActivityValidationError(
                    "Invalid opportunity for this organization.",
                )

    @staticmethod
    def _validate_activity_dates(
        *,
        status: ActivityStatus,
        due_at: datetime | None,
        completed_at: datetime | None,
    ) -> None:
        """
        Validate activity lifecycle timestamps.

        A completed activity must have a completion timestamp.
        An incomplete activity cannot retain one.
        """

        if (
            status == ActivityStatus.COMPLETED
            and completed_at is None
        ):
            raise ActivityValidationError(
                "completed_at is required when activity status "
                "is completed.",
            )

        if (
            status != ActivityStatus.COMPLETED
            and completed_at is not None
        ):
            raise ActivityValidationError(
                "completed_at can only be set when activity "
                "status is completed.",
            )

        if (
            due_at is not None
            and completed_at is not None
            and completed_at < due_at
        ):
            raise ActivityValidationError(
                "completed_at cannot be earlier than due_at.",
            )


__all__ = [
    "ActivityNotFoundError",
    "ActivityService",
    "ActivityValidationError",
]