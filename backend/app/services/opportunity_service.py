"""
==========================================================
NIVAG AI Business Automation

Opportunity Service

Business logic for tenant-scoped CRM opportunities.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from typing import Sequence
from uuid import UUID

from app.models.company import Company
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.opportunity import Opportunity
from app.repositories.opportunity_repository import OpportunityRepository
from app.schemas.opportunity.create import OpportunityCreate
from app.schemas.opportunity.update import OpportunityUpdate


class OpportunityNotFoundError(LookupError):
    """Raised when an opportunity cannot be found."""


class OpportunityValidationError(ValueError):
    """Raised when opportunity references are invalid."""


class OpportunityService:
    """
    Application service for tenant-scoped CRM opportunity
    operations.

    All read and write operations are scoped to a single
    organization.
    """

    def __init__(
        self,
        repository: OpportunityRepository,
    ) -> None:
        self._repository = repository

    async def create_opportunity(
        self,
        *,
        organization_id: UUID,
        data: OpportunityCreate,
    ) -> Opportunity:
        """
        Create a new opportunity inside an organization.

        Any referenced lead, company, or contact must belong
        to the same organization.
        """

        await self._validate_references(
            organization_id=organization_id,
            lead_id=data.lead_id,
            company_id=data.company_id,
            contact_id=data.contact_id,
        )

        opportunity = Opportunity(
            organization_id=organization_id,
            lead_id=data.lead_id,
            company_id=data.company_id,
            contact_id=data.contact_id,
            name=data.name,
            stage=data.stage,
            amount=data.amount,
            currency=data.currency,
            description=data.description,
        )

        return await self._repository.create(
            opportunity=opportunity,
        )

    async def get_opportunity(
        self,
        *,
        organization_id: UUID,
        opportunity_id: UUID,
    ) -> Opportunity:
        """
        Return one opportunity belonging to an organization.
        """

        opportunity = await self._repository.get_by_id(
            organization_id=organization_id,
            opportunity_id=opportunity_id,
        )

        if opportunity is None:
            raise OpportunityNotFoundError(
                "Opportunity not found."
            )

        return opportunity

    async def list_opportunities(
        self,
        *,
        organization_id: UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Opportunity]:
        """
        Return opportunities belonging to an organization.
        """

        return await self._repository.list(
            organization_id=organization_id,
            offset=offset,
            limit=limit,
        )

    async def update_opportunity(
        self,
        *,
        organization_id: UUID,
        opportunity_id: UUID,
        data: OpportunityUpdate,
    ) -> Opportunity:
        """
        Update an existing opportunity.

        Only explicitly supplied fields are updated.
        """

        opportunity = await self.get_opportunity(
            organization_id=organization_id,
            opportunity_id=opportunity_id,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        lead_id = update_data.get(
            "lead_id",
            opportunity.lead_id,
        )
        company_id = update_data.get(
            "company_id",
            opportunity.company_id,
        )
        contact_id = update_data.get(
            "contact_id",
            opportunity.contact_id,
        )

        await self._validate_references(
            organization_id=organization_id,
            lead_id=lead_id,
            company_id=company_id,
            contact_id=contact_id,
        )

        for field, value in update_data.items():
            setattr(
                opportunity,
                field,
                value,
            )

        return await self._repository.update(
            opportunity=opportunity,
        )

    async def delete_opportunity(
        self,
        *,
        organization_id: UUID,
        opportunity_id: UUID,
    ) -> None:
        """
        Delete an opportunity belonging to an organization.
        """

        opportunity = await self.get_opportunity(
            organization_id=organization_id,
            opportunity_id=opportunity_id,
        )

        await self._repository.delete(
            opportunity=opportunity,
        )

    async def _validate_references(
        self,
        *,
        organization_id: UUID,
        lead_id: UUID | None,
        company_id: UUID | None,
        contact_id: UUID | None,
    ) -> None:
        """
        Validate that all referenced CRM entities belong to
        the same organization as the opportunity.
        """

        session = self._repository.session

        if lead_id is not None:
            lead = await session.get(
                Lead,
                lead_id,
            )

            if (
                lead is None
                or lead.organization_id != organization_id
            ):
                raise OpportunityValidationError(
                    "Invalid lead for this organization."
                )

        if company_id is not None:
            company = await session.get(
                Company,
                company_id,
            )

            if (
                company is None
                or company.organization_id != organization_id
            ):
                raise OpportunityValidationError(
                    "Invalid company for this organization."
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
                raise OpportunityValidationError(
                    "Invalid contact for this organization."
                )


__all__ = [
    "OpportunityNotFoundError",
    "OpportunityService",
    "OpportunityValidationError",
]