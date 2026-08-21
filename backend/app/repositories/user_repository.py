"""
==========================================================
NIVAG AI Business Automation

User Repository

Description:
Persistence operations for application users.

Repository responsibilities:
- User database reads
- User database writes
- Query construction
- Entity persistence

Transaction ownership remains with the service layer.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """
    Repository for User persistence operations.

    The repository never commits or rolls back transactions.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        """
        Return a user by primary key.
        """

        statement = select(User).where(
            User.id == user_id,
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def get_by_organization_and_email(
        self,
        organization_id: UUID,
        email: str,
    ) -> User | None:
        """
        Return a user by organization and email.

        Email uniqueness is scoped to the organization.
        """

        statement = select(User).where(
            User.organization_id == organization_id,
            User.email == email,
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> list[User]:
        """
        Return all users matching an email address.

        Email is intentionally not globally unique because the
        database uniqueness constraint is organization-scoped.
        """

        statement = (
            select(User)
            .where(
                User.email == email,
            )
            .order_by(
                User.created_at.asc(),
                User.id.asc(),
            )
        )

        result = await self._session.execute(
            statement,
        )

        return list(
            result.scalars().all(),
        )

    async def list_by_organization(
        self,
        organization_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        Return users belonging to an organization using
        deterministic pagination.
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
            select(User)
            .where(
                User.organization_id == organization_id,
            )
            .order_by(
                User.created_at.asc(),
                User.id.asc(),
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
        user: User,
    ) -> User:
        """
        Stage a user for insertion.

        The transaction is not committed here.
        """

        self._session.add(
            user,
        )

        await self._session.flush()

        return user

    async def update(
        self,
        user: User,
    ) -> User:
        """
        Flush changes to an existing user.

        SQLAlchemy tracks the entity automatically.

        The transaction is not committed here.
        """

        await self._session.flush()

        return user

    async def delete(
        self,
        user: User,
    ) -> bool:
        """
        Delete an existing user.

        Returns:
            True when the user exists and is staged for deletion.
            False when no persisted user exists with the given ID.

        The transaction is not committed here.
        """

        existing = await self.get_by_id(
            user.id,
        )

        if existing is None:
            return False

        await self._session.delete(
            existing,
        )

        await self._session.flush()

        return True


__all__ = [
    "UserRepository",
]