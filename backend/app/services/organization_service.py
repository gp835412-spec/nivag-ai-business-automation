"""
==========================================================
NIVAG AI Business Automation

Organization Service

Business logic for organization management.

Responsibilities:
- Organization creation
- Organization lookup
- Organization updates
- Organization deletion
- Slug and email uniqueness validation
- Organization data normalization

Transaction boundaries remain under the control of the
calling application workflow.

Repository responsibilities remain limited to persistence.
==========================================================
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.repositories.organization_repository import (
    OrganizationRepository,
)


class OrganizationService:
    """
    Application service for Organization operations.

    The service owns organization business rules,
    normalization, validation, and uniqueness checks.

    Database queries and persistence remain inside the
    repository layer.

    Transaction ownership remains with the calling
    application workflow.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

        self._repository = OrganizationRepository(
            session,
        )

    async def create(
        self,
        organization: Organization | None = None,
        *,
        name: str | None = None,
        slug: str | None = None,
        legal_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        timezone: str = "Asia/Kolkata",
        currency: str = "INR",
    ) -> Organization:
        """
        Create and stage a new organization.

        Supports both application workflows:

        1. Passing a pre-built Organization instance.
        2. Passing organization fields directly.

        The organization is normalized and flushed but not
        committed.
        """

        if organization is not None:
            if any(
                value is not None
                for value in (
                    name,
                    slug,
                    legal_name,
                    email,
                    phone,
                )
            ):
                raise ValueError(
                    "Provide either an Organization instance or "
                    "organization fields, not both."
                )

            self._normalize_organization(
                organization,
            )

        else:
            normalized_name = (
                self._normalize_required_text(
                    name,
                    "name",
                )
            )

            normalized_slug = self._normalize_slug(
                slug,
            )

            normalized_currency = (
                self._normalize_currency(
                    currency,
                )
            )

            normalized_email = self._normalize_email(
                email,
            )

            normalized_legal_name = (
                self._normalize_optional_text(
                    legal_name,
                )
            )

            normalized_phone = (
                self._normalize_optional_text(
                    phone,
                )
            )

            normalized_timezone = (
                self._normalize_required_text(
                    timezone,
                    "timezone",
                )
            )

            organization = Organization(
                name=normalized_name,
                slug=normalized_slug,
                legal_name=normalized_legal_name,
                email=normalized_email,
                phone=normalized_phone,
                timezone=normalized_timezone,
                currency=normalized_currency,
            )

        existing_slug = await self._repository.get_by_slug(
            organization.slug,
        )

        if existing_slug is not None:
            raise ValueError(
                "An organization with this slug already exists."
            )

        existing_email = await self._repository.get_by_email(
            organization.email,
        )

        if existing_email is not None:
            raise ValueError(
                "An organization with this email already exists."
            )

        try:
            return await self._repository.add(
                organization,
            )

        except IntegrityError as exc:
            raise ValueError(
                "Organization could not be created because one or "
                "more unique values already exist."
            ) from exc

    async def get_by_id(
        self,
        organization_id: UUID,
    ) -> Organization | None:
        """
        Return an organization by primary key.
        """

        return await self._repository.get_by_id(
            organization_id,
        )

    async def get_by_slug(
        self,
        slug: str,
    ) -> Organization | None:
        """
        Return an organization by normalized slug.
        """

        normalized_slug = self._normalize_slug(
            slug,
        )

        return await self._repository.get_by_slug(
            normalized_slug,
        )

    async def get_by_email(
        self,
        email: str,
    ) -> Organization | None:
        """
        Return an organization by normalized email.
        """

        normalized_email = self._normalize_email(
            email,
        )

        return await self._repository.get_by_email(
            normalized_email,
        )

    async def list_all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Organization]:
        """
        Return organizations using validated pagination.
        """

        if offset < 0:
            raise ValueError(
                "offset cannot be negative."
            )

        if limit < 1:
            raise ValueError(
                "limit must be greater than zero."
            )

        return await self._repository.list_all(
            offset=offset,
            limit=limit,
        )

    async def update(
        self,
        organization: Organization,
    ) -> Organization:
        """
        Normalize, validate, and update an organization.

        Slug and email uniqueness are enforced before
        persistence.
        """

        self._normalize_organization(
            organization,
        )

        existing_slug = await self._repository.get_by_slug(
            organization.slug,
        )

        if (
            existing_slug is not None
            and existing_slug.id != organization.id
        ):
            raise ValueError(
                "An organization with this slug already exists."
            )

        existing_email = await self._repository.get_by_email(
            organization.email,
        )

        if (
            existing_email is not None
            and existing_email.id != organization.id
        ):
            raise ValueError(
                "An organization with this email already exists."
            )

        try:
            return await self._repository.update(
                organization,
            )

        except IntegrityError as exc:
            raise ValueError(
                "Organization could not be updated because one or "
                "more unique values already exists."
            ) from exc

    async def delete(
        self,
        organization: Organization,
    ) -> bool:
        """
        Delete an existing organization.

        The deletion is flushed but not committed.
        """

        return await self._repository.delete(
            organization,
        )

    def _normalize_organization(
        self,
        organization: Organization,
    ) -> None:
        """
        Normalize all mutable organization fields.
        """

        organization.name = (
            self._normalize_required_text(
                organization.name,
                "name",
            )
        )

        organization.slug = self._normalize_slug(
            organization.slug,
        )

        organization.legal_name = (
            self._normalize_optional_text(
                organization.legal_name,
            )
        )

        organization.email = self._normalize_email(
            organization.email,
        )

        organization.phone = (
            self._normalize_optional_text(
                organization.phone,
            )
        )

        organization.timezone = (
            self._normalize_required_text(
                organization.timezone,
                "timezone",
            )
        )

        organization.currency = (
            self._normalize_currency(
                organization.currency,
            )
        )

    @staticmethod
    def _normalize_required_text(
        value: str | None,
        field_name: str,
    ) -> str:
        """
        Normalize and validate a required text field.
        """

        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                f"{field_name} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty."
            )

        return normalized

    @staticmethod
    def _normalize_optional_text(
        value: str | None,
    ) -> str | None:
        """
        Normalize an optional text field.
        """

        if value is None:
            return None

        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                "Value must be a string."
            )

        normalized = value.strip()

        return normalized or None

    @staticmethod
    def _normalize_slug(
        slug: str | None,
    ) -> str:
        """
        Normalize and validate an organization slug.
        """

        if not isinstance(
            slug,
            str,
        ):
            raise ValueError(
                "slug must be a string."
            )

        normalized = slug.strip().lower()

        if not normalized:
            raise ValueError(
                "slug cannot be empty."
            )

        return normalized

    @staticmethod
    def _normalize_email(
        email: str | None,
    ) -> str:
        """
        Normalize and validate an organization email.
        """

        if not isinstance(
            email,
            str,
        ):
            raise ValueError(
                "email must be a string."
            )

        normalized = email.strip().lower()

        if not normalized:
            raise ValueError(
                "email cannot be empty."
            )

        return normalized

    @staticmethod
    def _normalize_currency(
        currency: str | None,
    ) -> str:
        """
        Normalize and validate an ISO-style currency code.
        """

        if not isinstance(
            currency,
            str,
        ):
            raise ValueError(
                "currency must be a string."
            )

        normalized = currency.strip().upper()

        if len(normalized) != 3:
            raise ValueError(
                "currency must contain exactly 3 characters."
            )

        return normalized


__all__ = [
    "OrganizationService",
]