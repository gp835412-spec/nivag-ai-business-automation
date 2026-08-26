"""
==========================================================
NIVAG AI Business Automation

Contact Repository

Database access layer for tenant-scoped CRM contacts.

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

from app.models.contact import Contact


class ContactRepository:
    """
    Repository for tenant-scoped CRM contact persistence.

    All organization-owned queries require organization_id
    to preserve tenant isolation.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        contact: Contact,
    ) -> Contact:
        """
        Persist a new contact.
        """

        self._session.add(contact)

        await self._session.flush()
        await self._session.refresh(contact)

        return contact

    async def get_by_id(
        self,
        *,
        contact_id: UUID,
        organization_id: UUID,
    ) -> Contact | None:
        """
        Return a contact only if it belongs to the given
        organization.
        """

        statement = select(Contact).where(
            Contact.id == contact_id,
            Contact.organization_id == organization_id,
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
    ) -> list[Contact]:
        """
        Return paginated contacts belonging to an organization.

        Contacts are ordered deterministically by creation
        time and identifier.
        """

        statement = (
            select(Contact)
            .where(
                Contact.organization_id == organization_id,
            )
            .order_by(
                Contact.created_at.desc(),
                Contact.id.desc(),
            )
            .limit(limit)
            .offset(offset)
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
        Return the total number of contacts belonging to an
        organization.
        """

        statement = select(
            func.count(Contact.id),
        ).where(
            Contact.organization_id == organization_id,
        )

        result = await self._session.execute(
            statement,
        )

        return int(
            result.scalar_one(),
        )

    async def update(
        self,
        contact: Contact,
    ) -> Contact:
        """
        Persist changes to an existing contact.
        """

        await self._session.flush()
        await self._session.refresh(contact)

        return contact

    async def delete(
        self,
        contact: Contact,
    ) -> None:
        """
        Delete an existing contact.
        """

        await self._session.delete(contact)

        await self._session.flush()


__all__ = [
    "ContactRepository",
]