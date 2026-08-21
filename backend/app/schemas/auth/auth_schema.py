"""
==========================================================
NIVAG AI Business Automation

Authentication Schemas

Request and response contracts for authentication flows.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from app.models.user import UserRole, UserStatus


class RegisterRequest(BaseModel):
    """Request payload for registering a new organization owner."""

    organization_name: str = Field(
        min_length=1,
        max_length=150,
    )

    organization_slug: str = Field(
        min_length=1,
        max_length=150,
    )

    legal_name: str | None = Field(
        default=None,
        max_length=200,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    first_name: str = Field(
        min_length=1,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        max_length=32,
    )

    timezone: str = Field(
        default="Asia/Kolkata",
        min_length=1,
        max_length=64,
    )

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )

    @field_validator(
        "organization_name",
        "organization_slug",
        "first_name",
        "timezone",
        mode="before",
    )
    @classmethod
    def normalize_required_text(
        cls,
        value: str,
    ) -> str:
        """Normalize required textual fields."""

        if not isinstance(value, str):
            raise ValueError("Value must be a string.")

        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty.")

        return value

    @field_validator("organization_slug")
    @classmethod
    def normalize_slug(
        cls,
        value: str,
    ) -> str:
        """Normalize organization slug."""

        return value.lower()

    @field_validator("currency")
    @classmethod
    def normalize_currency(
        cls,
        value: str,
    ) -> str:
        """Normalize currency code."""

        value = value.strip().upper()

        if len(value) != 3:
            raise ValueError(
                "currency must contain exactly 3 characters.",
            )

        return value

    @field_validator(
        "legal_name",
        "last_name",
        "phone",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        """Normalize optional text fields."""

        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError("Value must be a string.")

        value = value.strip()

        return value or None


class LoginRequest(BaseModel):
    """Request payload for user authentication."""

    organization_slug: str = Field(
        min_length=1,
        max_length=150,
    )

    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128,
    )

    @field_validator(
        "organization_slug",
        mode="before",
    )
    @classmethod
    def normalize_organization_slug(
        cls,
        value: str,
    ) -> str:
        """Normalize organization slug."""

        if not isinstance(value, str):
            raise ValueError("Value must be a string.")

        value = value.strip().lower()

        if not value:
            raise ValueError(
                "organization_slug cannot be empty.",
            )

        return value


class TokenResponse(BaseModel):
    """Authentication token response."""

    access_token: str

    token_type: str = "bearer"


class AuthenticatedUserResponse(BaseModel):
    """Public representation of the authenticated user."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    organization_id: UUID
    email: EmailStr
    first_name: str
    last_name: str | None
    phone: str | None
    role: UserRole
    status: UserStatus
    is_email_verified: bool


class LoginResponse(BaseModel):
    """Response returned after successful authentication."""

    access_token: str

    token_type: str = "bearer"

    user: AuthenticatedUserResponse


__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "AuthenticatedUserResponse",
    "LoginResponse",
]