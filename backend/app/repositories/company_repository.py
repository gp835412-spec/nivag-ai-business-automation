"""
==========================================================
NIVAG AI Business Automation

Company Repository

Database access layer for tenant-scoped CRM companies.

All read and write operations are scoped by organization_id
to preserve multi-tenant data isolation.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company


class CompanyRepository:
    """
    Repository responsible for Company database operations.

    Every operation that accesses a company requires the
    organization_id tenant boundary.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        *,
        organization_id: UUID,
        **company_data: object,
    ) -> Company:
        """
        Create a company inside an organization.
        """

        company = Company(
            organization_id=organization_id,
            **company_data,
        )

        self._session.add(company)

        await self._session.flush()
        await self._session.refresh(company)

        return company

    async def get_by_id(
        self,
        *,
        company_id: UUID,
        organization_id: UUID,
    ) -> Company | None:
        """
        Return a company only if it belongs to organization_id.
        """

        statement = select(Company).where(
            Company.id == company_id,
            Company.organization_id == organization_id,
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        organization_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Company]:
        """
        Return paginated companies for one organization.
        """

        statement = (
            select(Company)
            .where(
                Company.organization_id == organization_id,
            )
            .order_by(
                Company.created_at.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def count(
        self,
        *,
        organization_id: UUID,
    ) -> int:
        """
        Return the total number of companies for one organization.
        """

        statement = (
            select(func.count())
            .select_from(Company)
            .where(
                Company.organization_id == organization_id,
            )
        )

        result = await self._session.execute(statement)

        return int(result.scalar_one())

    async def update(
        self,
        company: Company,
        **company_data: object,
    ) -> Company:
        """
        Update an already tenant-validated company.
        """

        for field, value in company_data.items():
            setattr(
                company,
                field,
                value,
            )

        await self._session.flush()
        await self._session.refresh(company)

        return company

    async def delete(
        self,
        company: Company,
    ) -> None:
        """
        Delete an already tenant-validated company.
        """

        await self._session.delete(company)
        await self._session.flush()


__all__ = [
    "CompanyRepository",
]