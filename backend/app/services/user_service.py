"""
==========================================================
NIVAG AI Business Automation

User Service

Business logic for application users.

Responsibilities:
- User creation
- User lookup
- User updates
- User deletion
- Organization-scoped uniqueness validation
- Password hashing

Transaction boundaries remain under the control of the
calling application workflow.

Repository responsibilities remain limited to persistence.
==========================================================
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.security.password import hash_password


class UserService:
    """
    Application service for User operations.

    The service owns user business rules and validation.

    Database queries and persistence remain inside the
    repository layer.

    Transaction ownership remains with the calling
    application workflow so multiple services can participate
    in one atomic transaction.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

        self._repository = UserRepository(
            session,
        )

    async def create(
        self,
        *,
        organization_id: UUID,
        email: str,
        password: str,
        first_name: str,
        last_name: str | None = None,
        phone: str | None = None,
        role: UserRole = UserRole.MEMBER,
        status: UserStatus = UserStatus.ACTIVE,
        is_email_verified: bool = False,
    ) -> User:
        """
        Create and stage a new user inside an organization.

        The user is flushed but not committed.

        Raises:
            ValueError:
                If the email already exists in the organization
                or persistence detects an integrity conflict.
        """

        normalized_email = self._normalize_email(
            email,
        )

        normalized_first_name = (
            self._normalize_required_text(
                first_name,
                "first_name",
            )
        )

        normalized_last_name = (
            self._normalize_optional_text(
                last_name,
            )
        )

        normalized_phone = (
            self._normalize_optional_text(
                phone,
            )
        )

        existing = (
            await self._repository
            .get_by_organization_and_email(
                organization_id,
                normalized_email,
            )
        )

        if existing is not None:
            raise ValueError(
                "A user with this email already exists in the "
                "organization."
            )

        user = User(
            organization_id=organization_id,
            email=normalized_email,
            password_hash=hash_password(
                password,
            ),
            first_name=normalized_first_name,
            last_name=normalized_last_name,
            phone=normalized_phone,
            role=role,
            status=status,
            is_email_verified=is_email_verified,
        )

        try:
            return await self._repository.add(
                user,
            )

        except IntegrityError as exc:
            raise ValueError(
                "User could not be created because one or more "
                "unique values already exist."
            ) from exc

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        """
        Return a user by primary key.
        """

        return await self._repository.get_by_id(
            user_id,
        )

    async def get_by_organization_and_email(
        self,
        organization_id: UUID,
        email: str,
    ) -> User | None:
        """
        Return a user within an organization by email.
        """

        normalized_email = self._normalize_email(
            email,
        )

        return (
            await self._repository
            .get_by_organization_and_email(
                organization_id,
                normalized_email,
            )
        )

    async def get_by_email(
        self,
        email: str,
    ) -> list[User]:
        """
        Return all users matching an email.
        """

        normalized_email = self._normalize_email(
            email,
        )

        return await self._repository.get_by_email(
            normalized_email,
        )

    async def list_by_organization(
        self,
        organization_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        Return users belonging to an organization.
        """

        return await self._repository.list_by_organization(
            organization_id,
            offset=offset,
            limit=limit,
        )

    async def update(
        self,
        user: User,
        *,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        role: UserRole | None = None,
        status: UserStatus | None = None,
        is_email_verified: bool | None = None,
    ) -> User:
        """
        Update an existing user.

        Email uniqueness is enforced within the organization.

        The update is flushed but not committed.

        Raises:
            ValueError:
                If the requested email belongs to another user in
                the same organization or persistence detects an
                integrity conflict.
        """

        if email is not None:
            normalized_email = self._normalize_email(
                email,
            )

            if normalized_email != user.email:
                existing = (
                    await self._repository
                    .get_by_organization_and_email(
                        user.organization_id,
                        normalized_email,
                    )
                )

                if (
                    existing is not None
                    and existing.id != user.id
                ):
                    raise ValueError(
                        "A user with this email already exists in "
                        "the organization."
                    )

                user.email = normalized_email

        if first_name is not None:
            user.first_name = (
                self._normalize_required_text(
                    first_name,
                    "first_name",
                )
            )

        if last_name is not None:
            user.last_name = (
                self._normalize_optional_text(
                    last_name,
                )
            )

        if phone is not None:
            user.phone = self._normalize_optional_text(
                phone,
            )

        if role is not None:
            user.role = role

        if status is not None:
            user.status = status

        if is_email_verified is not None:
            user.is_email_verified = (
                is_email_verified
            )

        try:
            return await self._repository.update(
                user,
            )

        except IntegrityError as exc:
            raise ValueError(
                "User could not be updated because one or more "
                "unique values already exist."
            ) from exc

    async def delete(
        self,
        user: User,
    ) -> bool:
        """
        Delete an existing user.

        The deletion is flushed but not committed.
        """

        return await self._repository.delete(
            user,
        )

    @staticmethod
    def _normalize_email(
        email: str,
    ) -> str:
        """
        Normalize and validate an email value.
        """

        if not isinstance(
            email,
            str,
        ):
            raise ValueError(
                "email must be a string.",
            )

        normalized = email.strip().lower()

        if not normalized:
            raise ValueError(
                "email must not be empty.",
            )

        return normalized

    @staticmethod
    def _normalize_required_text(
        value: str,
        field_name: str,
    ) -> str:
        """
        Normalize a required text field.
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
                f"{field_name} must not be empty."
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
                "Value must be a string.",
            )

        normalized = value.strip()

        return normalized or None


__all__ = [
    "UserService",
]