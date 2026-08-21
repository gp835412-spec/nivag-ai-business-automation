"""
==========================================================
NIVAG AI Business Automation

Organization Repository

Description:
Persistence operations for organization entities.

Repository responsibilities:
- Database reads
- Database writes
- Query construction
- Entity persistence

Business rules and transaction orchestration belong to
the service layer.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization


class OrganizationRepository:
    """
    Repository for Organization persistence operations.

    The repository does not commit or rollback transactions.
    Transaction ownership remains with the service/application
    layer.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def get_by_id(
        self,
        organization_id: UUID,
    ) -> Organization | None:
        """
        Return an organization by primary key.

        Returns:
            Organization when found, otherwise None.
        """

        statement = select(Organization).where(
            Organization.id == organization_id,
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def get_by_slug(
        self,
        slug: str,
    ) -> Organization | None:
        """
        Return an organization by its unique slug.

        Returns:
            Organization when found, otherwise None.
        """

        statement = select(Organization).where(
            Organization.slug == slug,
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> Organization | None:
        """
        Return an organization by its contact email.

        The organization email is not globally unique at the
        database level, therefore this method intentionally
        returns only when exactly one row matches.
        """

        statement = select(Organization).where(
            Organization.email == email,
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def list_all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Organization]:
        """
        Return organizations using deterministic pagination.

        Args:
            offset: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of organizations ordered by creation time and
            UUID for deterministic pagination.
        """

        if offset < 0:
            raise ValueError(
                "offset must be greater than or equal to zero.",
            )

        if limit < 1 or limit > 1000:
            raise ValueError(
                "limit must be between 1 and 1000.",
            )

        statement = (
            select(Organization)
            .order_by(
                Organization.created_at.asc(),
                Organization.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self._session.execute(
            statement,
        )

        return list(
            result.scalars().all(),
        )

    async def add(
        self,
        organization: Organization,
    ) -> Organization:
        """
        Stage an organization for insertion.

        The transaction is not committed here.
        """

        self._session.add(
            organization,
        )

        await self._session.flush()

        return organization

    async def update(
        self,
        organization: Organization,
    ) -> Organization:
        """
        Persist changes made to an existing organization.

        SQLAlchemy tracks the entity automatically, so no explicit
        UPDATE statement is required here.

        The transaction is not committed here.

        The entity is explicitly refreshed after flush so
        database-generated values, including updated_at, are
        loaded before the entity is returned for API serialization.
        """

        await self._session.flush()

        await self._session.refresh(
            organization,
        )

        return organization

    async def delete(
        self,
        organization_id: UUID,
    ) -> bool:
        """
        Delete an organization by primary key.

        Returns:
            True when an organization was deleted,
            False when no matching organization existed.

        The transaction is not committed here.
        """

        statement = delete(Organization).where(
            Organization.id == organization_id,
        )

        result = await self._session.execute(
            statement,
        )

        return result.rowcount == 1


__all__ = [
    "OrganizationRepository",
]