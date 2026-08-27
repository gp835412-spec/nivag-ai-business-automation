"""
==========================================================
NIVAG AI Business Automation

Lead Schemas

Request and response schemas for tenant-scoped CRM leads.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class LeadStatus(StrEnum):
    """
    Lifecycle status of a CRM lead.
    """

    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class LeadBase(BaseModel):
    """
    Shared lead fields.
    """

    company_id: UUID | None = Field(
        default=None,
        description=(
            "Optional company associated with this lead."
        ),
    )

    contact_id: UUID | None = Field(
        default=None,
        description=(
            "Optional contact associated with this lead."
        ),
    )

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Lead title.",
    )

    first_name: str | None = Field(
        default=None,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        max_length=100,
    )

    email: EmailStr | None = Field(
        default=None,
    )

    phone: str | None = Field(
        default=None,
        max_length=32,
    )

    job_title: str | None = Field(
        default=None,
        max_length=150,
    )

    company_name: str | None = Field(
        default=None,
        max_length=200,
    )

    source: str | None = Field(
        default=None,
        max_length=100,
    )

    status: LeadStatus = Field(
        default=LeadStatus.NEW,
    )

    estimated_value: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=18,
        decimal_places=2,
    )

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )

    description: str | None = Field(
        default=None,
    )

    @field_validator(
        "title",
        mode="before",
    )
    @classmethod
    def normalize_required_title(
        cls,
        value: str,
    ) -> str:
        """
        Normalize the required lead title.
        """

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Lead title must not be empty.",
            )

        return normalized

    @field_validator(
        "first_name",
        "last_name",
        "phone",
        "job_title",
        "company_name",
        "source",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        """
        Strip whitespace and convert empty values to None.
        """

        if value is None:
            return None

        normalized = value.strip()

        return normalized or None

    @field_validator(
        "currency",
        mode="before",
    )
    @classmethod
    def normalize_currency(
        cls,
        value: str,
    ) -> str:
        """
        Normalize the ISO-style currency code.
        """

        normalized = value.strip().upper()

        if len(normalized) != 3:
            raise ValueError(
                "Currency must be a 3-letter code.",
            )

        return normalized


class LeadCreate(LeadBase):
    """
    Payload for creating a lead.

    organization_id is intentionally excluded because the
    organization is resolved from the authenticated user.
    """

    pass


class LeadUpdate(BaseModel):
    """
    Partial update payload for a lead.
    """

    company_id: UUID | None = Field(
        default=None,
    )

    contact_id: UUID | None = Field(
        default=None,
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    first_name: str | None = Field(
        default=None,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        max_length=100,
    )

    email: EmailStr | None = Field(
        default=None,
    )

    phone: str | None = Field(
        default=None,
        max_length=32,
    )

    job_title: str | None = Field(
        default=None,
        max_length=150,
    )

    company_name: str | None = Field(
        default=None,
        max_length=200,
    )

    source: str | None = Field(
        default=None,
        max_length=100,
    )

    status: LeadStatus | None = Field(
        default=None,
    )

    estimated_value: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=18,
        decimal_places=2,
    )

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    description: str | None = Field(
        default=None,
    )

    @field_validator(
        "title",
        mode="before",
    )
    @classmethod
    def normalize_optional_title(
        cls,
        value: str | None,
    ) -> str | None:
        """
        Normalize an optionally supplied lead title.
        """

        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Lead title must not be empty.",
            )

        return normalized

    @field_validator(
        "first_name",
        "last_name",
        "phone",
        "job_title",
        "company_name",
        "source",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        """
        Normalize optional text values.
        """

        if value is None:
            return None

        normalized = value.strip()

        return normalized or None

    @field_validator(
        "currency",
        mode="before",
    )
    @classmethod
    def normalize_optional_currency(
        cls,
        value: str | None,
    ) -> str | None:
        """
        Normalize an optionally supplied currency code.
        """

        if value is None:
            return None

        normalized = value.strip().upper()

        if len(normalized) != 3:
            raise ValueError(
                "Currency must be a 3-letter code.",
            )

        return normalized


class LeadResponse(BaseModel):
    """
    Lead API response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    organization_id: UUID

    company_id: UUID | None

    contact_id: UUID | None

    title: str

    first_name: str | None

    last_name: str | None

    email: EmailStr | None

    phone: str | None

    job_title: str | None

    company_name: str | None

    source: str | None

    status: LeadStatus

    estimated_value: Decimal | None

    currency: str

    description: str | None

    created_at: datetime

    updated_at: datetime


class LeadListResponse(BaseModel):
    """
    Paginated lead list response.
    """

    items: list[LeadResponse]

    total: int

    limit: int

    offset: int


__all__ = [
    "LeadCreate",
    "LeadListResponse",
    "LeadResponse",
    "LeadStatus",
    "LeadUpdate",
]