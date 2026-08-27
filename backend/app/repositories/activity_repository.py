"""
==========================================================
NIVAG AI Business Automation

Activity Repository

Persistence operations for tenant-scoped CRM activities.

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

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity


class ActivityRepository:
    """
    Repository for tenant-scoped Activity persistence operations.

    The repository does not commit or rollback transactions.
    Transaction ownership remains with the service/application
    layer.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    @property
    def session(self) -> AsyncSession:
        """
        Return the underlying database session.

        This is exposed for service-layer validation of related
        tenant-scoped CRM entities.
        """

        return self._session

    async def create(
        self,
        *,
        activity: Activity,
    ) -> Activity:
        """
        Stage and flush a new activity.

        The transaction is not committed here.
        """

        self._session.add(
            activity,
        )

        await self._session.flush()

        await self._session.refresh(
            activity,
        )

        return activity

    async def get_by_id(
        self,
        *,
        organization_id: UUID,
        activity_id: UUID,
    ) -> Activity | None:
        """
        Return one activity belonging to an organization.
        """

        statement = select(Activity).where(
            Activity.id == activity_id,
            Activity.organization_id == organization_id,
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
    ) -> Sequence[Activity]:
        """
        Return activities belonging to an organization.

        Activities are ordered deterministically by creation time
        and UUID.
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
            select(Activity)
            .where(
                Activity.organization_id == organization_id,
            )
            .order_by(
                Activity.created_at.asc(),
                Activity.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalars().all()

    async def update(
        self,
        *,
        activity: Activity,
    ) -> Activity:
        """
        Flush changes made to an existing activity.

        SQLAlchemy tracks the entity automatically, so no explicit
        UPDATE statement is required.

        The transaction is not committed here.
        """

        await self._session.flush()

        await self._session.refresh(
            activity,
        )

        return activity

    async def delete(
        self,
        *,
        activity: Activity,
    ) -> None:
        """
        Mark an activity for deletion.

        The transaction is not committed here.
        """

        await self._session.delete(
            activity,
        )

        await self._session.flush()


__all__ = [
    "ActivityRepository",
]