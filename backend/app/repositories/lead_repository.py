"""
==========================================================
NIVAG AI Business Automation

Lead Repository

Database access layer for tenant-scoped CRM leads.

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

from app.models.lead import Lead


class LeadRepository:
    """
    Repository for tenant-scoped lead persistence.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        lead: Lead,
    ) -> Lead:
        """
        Persist a new lead.
        """

        self._session.add(
            lead,
        )

        await self._session.commit()

        await self._session.refresh(
            lead,
        )

        return lead

    async def get_by_id(
        self,
        *,
        lead_id: UUID,
        organization_id: UUID,
    ) -> Lead | None:
        """
        Return a lead only when it belongs to the specified
        organization.
        """

        statement = select(
            Lead,
        ).where(
            Lead.id == lead_id,
            Lead.organization_id == organization_id,
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        organization_id: UUID,
        limit: int,
        offset: int,
    ) -> list[Lead]:
        """
        Return paginated leads for an organization.
        """

        statement = (
            select(
                Lead,
            )
            .where(
                Lead.organization_id == organization_id,
            )
            .order_by(
                Lead.created_at.desc(),
                Lead.id.desc(),
            )
            .limit(
                limit,
            )
            .offset(
                offset,
            )
        )

        result = await self._session.execute(
            statement,
        )

        return list(
            result.scalars().all(),
        )

    async def count(
        self,
        *,
        organization_id: UUID,
    ) -> int:
        """
        Return the total number of leads for an organization.
        """

        statement = (
            select(
                func.count(),
            )
            .select_from(
                Lead,
            )
            .where(
                Lead.organization_id == organization_id,
            )
        )

        result = await self._session.execute(
            statement,
        )

        return int(
            result.scalar_one(),
        )

    async def update(
        self,
        lead: Lead,
    ) -> Lead:
        """
        Persist changes to an existing lead.
        """

        await self._session.commit()

        await self._session.refresh(
            lead,
        )

        return lead

    async def delete(
        self,
        lead: Lead,
    ) -> None:
        """
        Delete a lead.
        """

        await self._session.delete(
            lead,
        )

        await self._session.commit()


__all__ = [
    "LeadRepository",
]