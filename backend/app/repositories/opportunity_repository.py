"""
==========================================================
NIVAG AI Business Automation

Opportunity Repository

Database access layer for tenant-scoped CRM opportunities.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity import Opportunity


class OpportunityRepository:
    """
    Repository responsible for database operations on
    tenant-scoped CRM opportunities.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        opportunity: Opportunity,
    ) -> Opportunity:
        """
        Persist a new opportunity.

        The caller is responsible for transaction management.
        """

        self._session.add(
            opportunity,
        )

        await self._session.flush()

        await self._session.refresh(
            opportunity,
        )

        return opportunity

    async def get_by_id(
        self,
        *,
        organization_id: UUID,
        opportunity_id: UUID,
    ) -> Opportunity | None:
        """
        Return an opportunity by ID within the specified organization.
        """

        statement: Select[tuple[Opportunity]] = (
            select(
                Opportunity,
            ).where(
                Opportunity.id == opportunity_id,
                Opportunity.organization_id == organization_id,
            )
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        organization_id: UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Opportunity]:
        """
        Return a paginated list of opportunities belonging
        to an organization.
        """

        statement: Select[tuple[Opportunity]] = (
            select(
                Opportunity,
            )
            .where(
                Opportunity.organization_id == organization_id,
            )
            .order_by(
                Opportunity.created_at.desc(),
            )
            .offset(
                offset,
            )
            .limit(
                limit,
            )
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalars().all()

    async def update(
        self,
        opportunity: Opportunity,
    ) -> Opportunity:
        """
        Flush changes made to an existing opportunity.

        The caller is responsible for applying field changes
        and transaction management.
        """

        await self._session.flush()

        await self._session.refresh(
            opportunity,
        )

        return opportunity

    async def delete(
        self,
        opportunity: Opportunity,
    ) -> None:
        """
        Remove an opportunity from the current session.

        The caller is responsible for transaction management.
        """

        await self._session.delete(
            opportunity,
        )

        await self._session.flush()


__all__ = [
    "OpportunityRepository",
]