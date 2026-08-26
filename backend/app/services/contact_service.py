"""
==========================================================
NIVAG AI Business Automation

Contact Service

Business logic for tenant-scoped CRM contact operations.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from uuid import UUID

from app.models.company import Company
from app.models.contact import Contact
from app.repositories.company_repository import CompanyRepository
from app.repositories.contact_repository import ContactRepository
from app.schemas.contact.contact_schema import (
    ContactCreate,
    ContactListResponse,
    ContactResponse,
    ContactUpdate,
)


class ContactNotFoundError(ValueError):
    """Raised when a contact cannot be found."""


class ContactCompanyNotFoundError(ValueError):
    """Raised when the requested company is not available."""


class ContactService:
    """
    Service for tenant-scoped CRM contact operations.

    Contacts are always scoped to an organization. When a
    company_id is supplied, the company must belong to the
    same organization.
    """

    def __init__(
        self,
        contact_repository: ContactRepository,
        company_repository: CompanyRepository,
    ) -> None:
        self._contact_repository = contact_repository
        self._company_repository = company_repository

    async def create_contact(
        self,
        *,
        organization_id: UUID,
        payload: ContactCreate,
    ) -> ContactResponse:
        """
        Create a new contact inside an organization.
        """

        if payload.company_id is not None:
            await self._get_company_or_raise(
                company_id=payload.company_id,
                organization_id=organization_id,
            )

        contact = Contact(
            organization_id=organization_id,
            **payload.model_dump(),
        )

        created = await self._contact_repository.create(
            contact,
        )

        return ContactResponse.model_validate(
            created,
        )

    async def get_contact(
        self,
        *,
        contact_id: UUID,
        organization_id: UUID,
    ) -> ContactResponse:
        """
        Return a contact belonging to the organization.
        """

        contact = await self._contact_repository.get_by_id(
            contact_id=contact_id,
            organization_id=organization_id,
        )

        if contact is None:
            raise ContactNotFoundError(
                "Contact not found.",
            )

        return ContactResponse.model_validate(
            contact,
        )

    async def list_contacts(
        self,
        *,
        organization_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> ContactListResponse:
        """
        Return paginated contacts for an organization.
        """

        if offset < 0:
            raise ValueError(
                "offset must be greater than or equal to 0.",
            )

        if limit < 1 or limit > 100:
            raise ValueError(
                "limit must be between 1 and 100.",
            )

        contacts = await self._contact_repository.list(
            organization_id=organization_id,
            limit=limit,
            offset=offset,
        )

        total = await self._contact_repository.count(
            organization_id=organization_id,
        )

        return ContactListResponse(
            items=[
                ContactResponse.model_validate(contact)
                for contact in contacts
            ],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def update_contact(
        self,
        *,
        contact_id: UUID,
        organization_id: UUID,
        payload: ContactUpdate,
    ) -> ContactResponse:
        """
        Update a contact belonging to an organization.
        """

        contact = await self._contact_repository.get_by_id(
            contact_id=contact_id,
            organization_id=organization_id,
        )

        if contact is None:
            raise ContactNotFoundError(
                "Contact not found.",
            )

        update_data = payload.model_dump(
            exclude_unset=True,
        )

        if "company_id" in update_data:
            company_id = update_data["company_id"]

            if company_id is not None:
                await self._get_company_or_raise(
                    company_id=company_id,
                    organization_id=organization_id,
                )

        for field, value in update_data.items():
            setattr(
                contact,
                field,
                value,
            )

        updated = await self._contact_repository.update(
            contact,
        )

        return ContactResponse.model_validate(
            updated,
        )

    async def delete_contact(
        self,
        *,
        contact_id: UUID,
        organization_id: UUID,
    ) -> None:
        """
        Delete a contact belonging to an organization.
        """

        contact = await self._contact_repository.get_by_id(
            contact_id=contact_id,
            organization_id=organization_id,
        )

        if contact is None:
            raise ContactNotFoundError(
                "Contact not found.",
            )

        await self._contact_repository.delete(
            contact,
        )

    async def _get_company_or_raise(
        self,
        *,
        company_id: UUID,
        organization_id: UUID,
    ) -> Company:
        """
        Return a company only when it belongs to the same
        organization as the contact.
        """

        company = await self._company_repository.get_by_id(
            company_id=company_id,
            organization_id=organization_id,
        )

        if company is None:
            raise ContactCompanyNotFoundError(
                "Company not found.",
            )

        return company


__all__ = [
    "ContactCompanyNotFoundError",
    "ContactNotFoundError",
    "ContactService",
]