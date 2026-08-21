"""
==========================================================
NIVAG AI Business Automation

Organization Schemas

Description:
Pydantic request and response schemas for organization
management APIs.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from app.models.organization import OrganizationStatus


class OrganizationCreate(BaseModel):
    """
    Request schema for creating an organization.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    name: str = Field(
        min_length=1,
        max_length=150,
    )

    slug: str = Field(
        min_length=1,
        max_length=150,
    )

    legal_name: str | None = Field(
        default=None,
        max_length=200,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=32,
    )

    website: str | None = Field(
        default=None,
        max_length=500,
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

    description: str | None = None

    @field_validator(
        "name",
        "slug",
        "timezone",
        mode="before",
    )
    @classmethod
    def normalize_required_text(
        cls,
        value: str,
    ) -> str:
        """
        Normalize required textual fields.
        """

        if not isinstance(value, str):
            raise ValueError(
                "Value must be a string.",
            )

        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be empty.",
            )

        return value

    @field_validator(
        "legal_name",
        "phone",
        "website",
        "description",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        """
        Normalize optional textual fields.
        """

        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(
                "Value must be a string.",
            )

        value = value.strip()

        return value or None

    @field_validator("slug")
    @classmethod
    def normalize_slug(
        cls,
        value: str,
    ) -> str:
        """
        Normalize organization slug.
        """

        return value.lower()

    @field_validator("currency")
    @classmethod
    def normalize_currency(
        cls,
        value: str,
    ) -> str:
        """
        Normalize currency code.
        """

        if not isinstance(value, str):
            raise ValueError(
                "currency must be a string.",
            )

        value = value.strip().upper()

        if len(value) != 3:
            raise ValueError(
                "currency must contain exactly 3 characters.",
            )

        return value


class OrganizationUpdate(BaseModel):
    """
    Request schema for updating an organization.

    All fields are optional so partial updates are supported.

    Unknown fields are rejected to prevent accidental or
    unsupported organization attribute updates.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    legal_name: str | None = Field(
        default=None,
        max_length=200,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=32,
    )

    website: str | None = Field(
        default=None,
        max_length=500,
    )

    timezone: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
    )

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    status: OrganizationStatus | None = None

    description: str | None = None

    @field_validator(
        "name",
        "slug",
        "timezone",
        mode="before",
    )
    @classmethod
    def normalize_required_update_text(
        cls,
        value: str | None,
    ) -> str | None:
        """
        Normalize optional update text fields.
        """

        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(
                "Value must be a string.",
            )

        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be empty.",
            )

        return value

    @field_validator(
        "legal_name",
        "phone",
        "website",
        "description",
        mode="before",
    )
    @classmethod
    def normalize_optional_update_text(
        cls,
        value: str | None,
    ) -> str | None:
        """
        Normalize optional nullable fields.
        """

        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(
                "Value must be a string.",
            )

        value = value.strip()

        return value or None

    @field_validator("slug")
    @classmethod
    def normalize_update_slug(
        cls,
        value: str | None,
    ) -> str | None:
        """
        Normalize organization slug.
        """

        if value is None:
            return None

        return value.lower()

    @field_validator("currency")
    @classmethod
    def normalize_update_currency(
        cls,
        value: str | None,
    ) -> str | None:
        """
        Normalize currency code.
        """

        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(
                "currency must be a string.",
            )

        value = value.strip().upper()

        if len(value) != 3:
            raise ValueError(
                "currency must contain exactly 3 characters.",
            )

        return value


class OrganizationResponse(BaseModel):
    """
    API response schema for an organization.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    name: str
    slug: str
    legal_name: str | None
    email: EmailStr | None
    phone: str | None
    website: str | None
    timezone: str
    currency: str
    status: OrganizationStatus
    description: str | None
    created_at: datetime
    updated_at: datetime


class OrganizationListResponse(BaseModel):
    """
    Paginated organization collection response.
    """

    items: list[OrganizationResponse]
    offset: int
    limit: int
    count: int


__all__ = [
    "OrganizationCreate",
    "OrganizationUpdate",
    "OrganizationResponse",
    "OrganizationListResponse",
]