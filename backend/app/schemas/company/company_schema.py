"""
==========================================================
NIVAG AI Business Automation

Company Schemas

Request and response schemas for tenant-scoped CRM companies.

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
    HttpUrl,
    field_validator,
)


class CompanyBase(BaseModel):
    """
    Shared company fields.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    name: str = Field(
        min_length=1,
        max_length=200,
        description="Primary company name.",
    )

    legal_name: str | None = Field(
        default=None,
        max_length=250,
    )

    email: EmailStr | None = Field(
        default=None,
    )

    phone: str | None = Field(
        default=None,
        max_length=32,
    )

    website: HttpUrl | None = Field(
        default=None,
        max_length=500,
    )

    industry: str | None = Field(
        default=None,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
    )

    address_line_1: str | None = Field(
        default=None,
        max_length=200,
    )

    address_line_2: str | None = Field(
        default=None,
        max_length=200,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    postal_code: str | None = Field(
        default=None,
        max_length=32,
    )

    country: str | None = Field(
        default=None,
        max_length=100,
    )

    @field_validator(
        "name",
        mode="before",
    )
    @classmethod
    def normalize_required_name(
        cls,
        value: str,
    ) -> str:
        """Normalize the required company name."""

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Company name must not be empty.",
            )

        return normalized

    @field_validator(
        "legal_name",
        "phone",
        "industry",
        "address_line_1",
        "address_line_2",
        "city",
        "state",
        "postal_code",
        "country",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        """Strip whitespace and convert empty values to None."""

        if value is None:
            return None

        normalized = value.strip()

        return normalized or None


class CompanyCreate(CompanyBase):
    """
    Payload for creating a company.

    organization_id is intentionally excluded because the
    organization is resolved from the authenticated user.
    """

    pass


class CompanyUpdate(BaseModel):
    """
    Partial update payload for a company.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    legal_name: str | None = Field(
        default=None,
        max_length=250,
    )

    email: EmailStr | None = Field(
        default=None,
    )

    phone: str | None = Field(
        default=None,
        max_length=32,
    )

    website: HttpUrl | None = Field(
        default=None,
        max_length=500,
    )

    industry: str | None = Field(
        default=None,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
    )

    address_line_1: str | None = Field(
        default=None,
        max_length=200,
    )

    address_line_2: str | None = Field(
        default=None,
        max_length=200,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    postal_code: str | None = Field(
        default=None,
        max_length=32,
    )

    country: str | None = Field(
        default=None,
        max_length=100,
    )

    @field_validator(
        "name",
        mode="before",
    )
    @classmethod
    def normalize_optional_name(
        cls,
        value: str | None,
    ) -> str | None:
        """Normalize an optionally supplied company name."""

        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Company name must not be empty.",
            )

        return normalized

    @field_validator(
        "legal_name",
        "phone",
        "industry",
        "address_line_1",
        "address_line_2",
        "city",
        "state",
        "postal_code",
        "country",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        """Normalize optional text values."""

        if value is None:
            return None

        normalized = value.strip()

        return normalized or None


class CompanyResponse(BaseModel):
    """
    Company API response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    organization_id: UUID

    name: str

    legal_name: str | None

    email: EmailStr | None

    phone: str | None

    website: str | None

    industry: str | None

    description: str | None

    address_line_1: str | None

    address_line_2: str | None

    city: str | None

    state: str | None

    postal_code: str | None

    country: str | None

    created_at: datetime

    updated_at: datetime


class CompanyListResponse(BaseModel):
    """
    Paginated company list response.
    """

    items: list[CompanyResponse]

    total: int

    limit: int

    offset: int


__all__ = [
    "CompanyCreate",
    "CompanyListResponse",
    "CompanyResponse",
    "CompanyUpdate",
]