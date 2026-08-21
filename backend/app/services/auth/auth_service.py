"""
==========================================================
NIVAG AI Business Automation

Authentication Service

Responsibilities:
- Organization registration
- Owner user creation
- Login
- Password verification
- JWT access-token creation
- Authentication business rules
- Registration transaction orchestration

Transaction ownership for the registration workflow remains
inside this service.

Routes must not contain authentication business logic.
==========================================================
"""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User, UserRole, UserStatus
from app.security.password import verify_password
from app.security.token import create_access_token
from app.services.organization_service import OrganizationService
from app.services.user_service import UserService


class AuthenticationError(ValueError):
    """
    Raised when authentication fails.

    The message intentionally does not disclose whether the
    organization, user, or password was incorrect.
    """


class AuthService:
    """
    Application service for authentication workflows.

    The registration workflow owns a single database
    transaction covering both organization and owner-user
    creation.
    """

    INVALID_CREDENTIALS_MESSAGE = (
        "Invalid organization credentials."
    )

    INACTIVE_USER_MESSAGE = (
        "User account is not active."
    )

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

        self._organization_service = OrganizationService(
            session,
        )

        self._user_service = UserService(
            session,
        )

    async def register(
        self,
        *,
        organization_name: str,
        organization_slug: str,
        email: str,
        password: str,
        first_name: str,
        legal_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        timezone: str = "Asia/Kolkata",
        currency: str = "INR",
    ) -> User:
        """
        Register a new organization and its owner user.

        The complete registration workflow is atomic:

        1. Normalize registration input.
        2. Create and flush the organization.
        3. Create and flush the owner user.
        4. Commit once after both operations succeed.

        Any failure rolls back the entire workflow so a partial
        registration cannot remain in the database.
        """

        normalized_organization_name = (
            self._normalize_required_text(
                organization_name,
                "organization_name",
            )
        )

        normalized_organization_slug = (
            self._normalize_slug(
                organization_slug,
            )
        )

        normalized_email = (
            self._normalize_email(
                email,
            )
        )

        normalized_first_name = (
            self._normalize_required_text(
                first_name,
                "first_name",
            )
        )

        normalized_legal_name = (
            self._normalize_optional_text(
                legal_name,
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

        normalized_timezone = (
            self._normalize_required_text(
                timezone,
                "timezone",
            )
        )

        normalized_currency = (
            self._normalize_required_text(
                currency,
                "currency",
            ).upper()
        )

        organization = Organization(
            name=normalized_organization_name,
            slug=normalized_organization_slug,
            legal_name=normalized_legal_name,
            email=normalized_email,
            phone=normalized_phone,
            timezone=normalized_timezone,
            currency=normalized_currency,
        )

        try:
            created_organization = (
                await self._organization_service.create(
                    organization,
                )
            )

            user = await self._user_service.create(
                organization_id=created_organization.id,
                email=normalized_email,
                password=password,
                first_name=normalized_first_name,
                last_name=normalized_last_name,
                phone=normalized_phone,
                role=UserRole.OWNER,
                status=UserStatus.ACTIVE,
                is_email_verified=False,
            )

            await self._session.commit()

            await self._session.refresh(
                user,
            )

            return user

        except ValueError:
            await self._session.rollback()
            raise

        except IntegrityError as exc:
            await self._session.rollback()

            raise ValueError(
                "Registration could not be completed because "
                "a conflicting record already exists.",
            ) from exc

        except Exception:
            await self._session.rollback()
            raise

    async def _authenticate_credentials(
        self,
        *,
        organization_slug: str,
        email: str,
        password: str,
    ) -> User:
        """
        Authenticate credentials and return the user.
        """

        normalized_slug = self._normalize_slug(
            organization_slug,
        )

        normalized_email = self._normalize_email(
            email,
        )

        organization = (
            await self._organization_service.get_by_slug(
                normalized_slug,
            )
        )

        if organization is None:
            raise AuthenticationError(
                self.INVALID_CREDENTIALS_MESSAGE,
            )

        user = (
            await self._user_service
            .get_by_organization_and_email(
                organization.id,
                normalized_email,
            )
        )

        if user is None:
            raise AuthenticationError(
                self.INVALID_CREDENTIALS_MESSAGE,
            )

        if user.status != UserStatus.ACTIVE:
            raise AuthenticationError(
                self.INACTIVE_USER_MESSAGE,
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise AuthenticationError(
                self.INVALID_CREDENTIALS_MESSAGE,
            )

        return user

    async def authenticate_user(
        self,
        *,
        organization_slug: str,
        email: str,
        password: str,
    ) -> User:
        """
        Authenticate credentials and return the authenticated
        user.
        """

        return await self._authenticate_credentials(
            organization_slug=organization_slug,
            email=email,
            password=password,
        )

    async def login(
        self,
        *,
        organization_slug: str,
        email: str,
        password: str,
    ) -> str:
        """
        Authenticate a user and return a JWT access token.
        """

        user = await self._authenticate_credentials(
            organization_slug=organization_slug,
            email=email,
            password=password,
        )

        return create_access_token(
            str(user.id),
        )

    async def login_with_user(
        self,
        *,
        organization_slug: str,
        email: str,
        password: str,
    ) -> tuple[User, str]:
        """
        Authenticate a user and return both the authenticated
        user and JWT access token.
        """

        user = await self._authenticate_credentials(
            organization_slug=organization_slug,
            email=email,
            password=password,
        )

        token = create_access_token(
            str(user.id),
        )

        return user, token

    @staticmethod
    def _normalize_email(
        email: str,
    ) -> str:
        """
        Normalize and validate an email address.
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
    def _normalize_slug(
        slug: str,
    ) -> str:
        """
        Normalize and validate an organization slug.
        """

        if not isinstance(
            slug,
            str,
        ):
            raise ValueError(
                "organization_slug must be a string.",
            )

        normalized = slug.strip().lower()

        if not normalized:
            raise ValueError(
                "organization_slug must not be empty.",
            )

        return normalized

    @staticmethod
    def _normalize_required_text(
        value: str,
        field_name: str,
    ) -> str:
        """
        Normalize and validate a required text value.
        """

        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                f"{field_name} must be a string.",
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be empty.",
            )

        return normalized

    @staticmethod
    def _normalize_optional_text(
        value: str | None,
    ) -> str | None:
        """
        Normalize an optional text value.
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
    "AuthService",
    "AuthenticationError",
]