"""
==========================================================
NIVAG AI Business Automation

Company Service

Business logic layer for tenant-scoped CRM companies.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from uuid import UUID

from app.models.company import Company
from app.repositories.company_repository import CompanyRepository
from app.schemas.company.company_schema import (
    CompanyCreate,
    CompanyListResponse,
    CompanyResponse,
    CompanyUpdate,
)


class CompanyNotFoundError(ValueError):
    """Raised when a company does not exist in the organization."""


class CompanyService:
    """
    Business service for tenant-scoped company operations.

    Every company operation is constrained to an organization_id,
    ensuring multi-tenant data isolation.
    """

    def __init__(
        self,
        repository: CompanyRepository,
    ) -> None:
        self._repository = repository

    async def create_company(
        self,
        *,
        organization_id: UUID,
        payload: CompanyCreate,
    ) -> CompanyResponse:
        """Create a new company inside the current organization."""

        company_data = self._prepare_create_data(payload)

        company = await self._repository.create(
            organization_id=organization_id,
            **company_data,
        )

        return CompanyResponse.model_validate(company)

    async def get_company(
        self,
        *,
        company_id: UUID,
        organization_id: UUID,
    ) -> CompanyResponse:
        """Get one company belonging to the current organization."""

        company = await self._get_required_company(
            company_id=company_id,
            organization_id=organization_id,
        )

        return CompanyResponse.model_validate(company)

    async def list_companies(
        self,
        *,
        organization_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> CompanyListResponse:
        """Return paginated companies for one organization."""

        normalized_limit = self._normalize_limit(limit)
        normalized_offset = self._normalize_offset(offset)

        companies = await self._repository.list(
            organization_id=organization_id,
            limit=normalized_limit,
            offset=normalized_offset,
        )

        total = await self._repository.count(
            organization_id=organization_id,
        )

        return CompanyListResponse(
            items=[
                CompanyResponse.model_validate(company)
                for company in companies
            ],
            total=total,
            limit=normalized_limit,
            offset=normalized_offset,
        )

    async def update_company(
        self,
        *,
        company_id: UUID,
        organization_id: UUID,
        payload: CompanyUpdate,
    ) -> CompanyResponse:
        """Partially update a company inside the current organization."""

        company = await self._get_required_company(
            company_id=company_id,
            organization_id=organization_id,
        )

        update_data = self._prepare_update_data(payload)

        if update_data:
            company = await self._repository.update(
                company,
                **update_data,
            )

        return CompanyResponse.model_validate(company)

    async def delete_company(
        self,
        *,
        company_id: UUID,
        organization_id: UUID,
    ) -> None:
        """Delete a company belonging to the current organization."""

        company = await self._get_required_company(
            company_id=company_id,
            organization_id=organization_id,
        )

        await self._repository.delete(company)

    async def _get_required_company(
        self,
        *,
        company_id: UUID,
        organization_id: UUID,
    ) -> Company:
        """Resolve a company within the organization boundary."""

        company = await self._repository.get_by_id(
            company_id=company_id,
            organization_id=organization_id,
        )

        if company is None:
            raise CompanyNotFoundError(
                "Company not found.",
            )

        return company

    @staticmethod
    def _prepare_create_data(
        payload: CompanyCreate,
    ) -> dict[str, object]:
        """Convert a validated create payload into repository data."""

        data = payload.model_dump(
            exclude_unset=True,
        )

        return CompanyService._normalize_payload_data(data)

    @staticmethod
    def _prepare_update_data(
        payload: CompanyUpdate,
    ) -> dict[str, object]:
        """
        Convert a partial update payload into repository data.

        Fields not explicitly provided by the client are excluded.
        """

        data = payload.model_dump(
            exclude_unset=True,
        )

        return CompanyService._normalize_payload_data(data)

    @staticmethod
    def _normalize_payload_data(
        data: dict[str, object],
    ) -> dict[str, object]:
        """Convert schema-specific values into model-compatible values."""

        normalized: dict[str, object] = {}

        for field, value in data.items():
            if value is None:
                normalized[field] = None
                continue

            if field == "website":
                normalized[field] = str(value)
                continue

            normalized[field] = value

        return normalized

    @staticmethod
    def _normalize_limit(
        limit: int,
    ) -> int:
        """Enforce safe pagination boundaries."""

        if limit < 1:
            return 1

        if limit > 100:
            return 100

        return limit

    @staticmethod
    def _normalize_offset(
        offset: int,
    ) -> int:
        """Prevent negative pagination offsets."""

        if offset < 0:
            return 0

        return offset


__all__ = [
    "CompanyNotFoundError",
    "CompanyService",
]