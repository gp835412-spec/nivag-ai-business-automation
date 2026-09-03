"""
==========================================================
NIVAG AI Business Automation

Lead Service

Business logic for tenant-scoped CRM lead operations.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.automation import (
    AutomationDispatcher,
    AutomationEvent,
    AutomationEventType,
)
from app.models.company import Company
from app.models.contact import Contact
from app.models.lead import Lead
from app.repositories.company_repository import CompanyRepository
from app.repositories.contact_repository import ContactRepository
from app.repositories.lead_repository import LeadRepository
from app.schemas.lead.lead_schema import (
    LeadCreate,
    LeadListResponse,
    LeadResponse,
    LeadUpdate,
)


class LeadNotFoundError(ValueError):
    """Raised when a lead cannot be found."""


class LeadCompanyNotFoundError(ValueError):
    """Raised when the requested company is not available."""


class LeadContactNotFoundError(ValueError):
    """Raised when the requested contact is not available."""


class LeadService:
    """
    Service for tenant-scoped CRM lead operations.

    Leads always belong to an organization.

    Related companies and contacts must belong to the
    same organization.
    """

    def __init__(
        self,
        lead_repository: LeadRepository,
        company_repository: CompanyRepository,
        contact_repository: ContactRepository,
        automation_dispatcher: AutomationDispatcher,
    ) -> None:
        self._lead_repository = lead_repository
        self._company_repository = company_repository
        self._contact_repository = contact_repository
        self._automation_dispatcher = automation_dispatcher

    async def create_lead(
        self,
        *,
        organization_id: UUID,
        payload: LeadCreate,
    ) -> LeadResponse:
        """
        Create a new lead inside an organization.

        A lead.created automation event is dispatched only
        after the lead has been successfully persisted.
        """

        if payload.company_id is not None:
            await self._get_company_or_raise(
                company_id=payload.company_id,
                organization_id=organization_id,
            )

        if payload.contact_id is not None:
            await self._get_contact_or_raise(
                contact_id=payload.contact_id,
                organization_id=organization_id,
            )

        lead = Lead(
            organization_id=organization_id,
            **payload.model_dump(),
        )

        created = await self._lead_repository.create(
            lead,
        )

        await self._automation_dispatcher.dispatch(
            AutomationEvent(
                event_type=AutomationEventType.LEAD_CREATED,
                organization_id=created.organization_id,
                entity_id=created.id,
                occurred_at=datetime.now(
                    timezone.utc,
                ),
                payload={
                    "lead_id": str(created.id),
                    "organization_id": str(
                        created.organization_id,
                    ),
                    "title": created.title,
                    "status": created.status,
                },
            ),
        )

        return LeadResponse.model_validate(
            created,
        )

    async def get_lead(
        self,
        *,
        lead_id: UUID,
        organization_id: UUID,
    ) -> LeadResponse:
        """
        Return a lead belonging to the organization.
        """

        lead = await self._lead_repository.get_by_id(
            lead_id=lead_id,
            organization_id=organization_id,
        )

        if lead is None:
            raise LeadNotFoundError(
                "Lead not found.",
            )

        return LeadResponse.model_validate(
            lead,
        )

    async def list_leads(
        self,
        *,
        organization_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> LeadListResponse:
        """
        Return paginated leads for an organization.
        """

        if offset < 0:
            raise ValueError(
                "offset must be greater than or equal to 0.",
            )

        if limit < 1 or limit > 100:
            raise ValueError(
                "limit must be between 1 and 100.",
            )

        leads = await self._lead_repository.list(
            organization_id=organization_id,
            limit=limit,
            offset=offset,
        )

        total = await self._lead_repository.count(
            organization_id=organization_id,
        )

        return LeadListResponse(
            items=[
                LeadResponse.model_validate(
                    lead,
                )
                for lead in leads
            ],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def update_lead(
        self,
        *,
        lead_id: UUID,
        organization_id: UUID,
        payload: LeadUpdate,
    ) -> LeadResponse:
        """
        Update a lead belonging to an organization.

        A lead.updated event is dispatched after successful
        persistence.

        A lead.status_changed event is additionally dispatched
        when the lead status actually changes.
        """

        lead = await self._lead_repository.get_by_id(
            lead_id=lead_id,
            organization_id=organization_id,
        )

        if lead is None:
            raise LeadNotFoundError(
                "Lead not found.",
            )

        previous_status = lead.status

        update_data = payload.model_dump(
            exclude_unset=True,
        )

        company_id = update_data.get(
            "company_id",
        )

        if (
            "company_id" in update_data
            and company_id is not None
        ):
            await self._get_company_or_raise(
                company_id=company_id,
                organization_id=organization_id,
            )

        contact_id = update_data.get(
            "contact_id",
        )

        if (
            "contact_id" in update_data
            and contact_id is not None
        ):
            await self._get_contact_or_raise(
                contact_id=contact_id,
                organization_id=organization_id,
            )

        for field, value in update_data.items():
            setattr(
                lead,
                field,
                value,
            )

        status_changed = (
            "status" in update_data
            and previous_status != lead.status
        )

        updated = await self._lead_repository.update(
            lead,
        )

        await self._automation_dispatcher.dispatch(
            AutomationEvent(
                event_type=AutomationEventType.LEAD_UPDATED,
                organization_id=updated.organization_id,
                entity_id=updated.id,
                occurred_at=datetime.now(
                    timezone.utc,
                ),
                payload={
                    "lead_id": str(updated.id),
                    "organization_id": str(
                        updated.organization_id,
                    ),
                    "title": updated.title,
                    "status": updated.status,
                },
            ),
        )

        if status_changed:
            await self._automation_dispatcher.dispatch(
                AutomationEvent(
                    event_type=AutomationEventType.LEAD_STATUS_CHANGED,
                    organization_id=updated.organization_id,
                    entity_id=updated.id,
                    occurred_at=datetime.now(
                        timezone.utc,
                    ),
                    payload={
                        "lead_id": str(updated.id),
                        "organization_id": str(
                            updated.organization_id,
                        ),
                        "title": updated.title,
                        "previous_status": previous_status,
                        "new_status": updated.status,
                    },
                ),
            )

        return LeadResponse.model_validate(
            updated,
        )

    async def delete_lead(
        self,
        *,
        lead_id: UUID,
        organization_id: UUID,
    ) -> None:
        """
        Delete a lead belonging to the organization.
        """

        lead = await self._lead_repository.get_by_id(
            lead_id=lead_id,
            organization_id=organization_id,
        )

        if lead is None:
            raise LeadNotFoundError(
                "Lead not found.",
            )

        await self._lead_repository.delete(
            lead,
        )

    async def _get_company_or_raise(
        self,
        *,
        company_id: UUID,
        organization_id: UUID,
    ) -> Company:
        """
        Return a company only when it belongs to the same
        organization.
        """

        company = await self._company_repository.get_by_id(
            company_id=company_id,
            organization_id=organization_id,
        )

        if company is None:
            raise LeadCompanyNotFoundError(
                "Company not found.",
            )

        return company

    async def _get_contact_or_raise(
        self,
        *,
        contact_id: UUID,
        organization_id: UUID,
    ) -> Contact:
        """
        Return a contact only when it belongs to the same
        organization.
        """

        contact = await self._contact_repository.get_by_id(
            contact_id=contact_id,
            organization_id=organization_id,
        )

        if contact is None:
            raise LeadContactNotFoundError(
                "Contact not found.",
            )

        return contact


__all__ = [
    "LeadCompanyNotFoundError",
    "LeadContactNotFoundError",
    "LeadNotFoundError",
    "LeadService",
]