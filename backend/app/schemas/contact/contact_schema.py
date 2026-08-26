"""
==========================================================
NIVAG AI Business Automation

Contact Schemas

Request and response schemas for tenant-scoped CRM contacts.

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


class ContactBase(BaseModel):
    """
    Shared contact fields.
    """

    company_id: UUID | None = Field(
        default=None,
        description=(
            "Optional company associated with this contact."
        ),
    )

    first_name: str = Field(
        min_length=1,
        max_length=100,
        description="Contact first name.",
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

    department: str | None = Field(
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
        "first_name",
        mode="before",
    )
    @classmethod
    def normalize_required_first_name(
        cls,
        value: str,
    ) -> str:
        """
        Normalize the required contact first name.
        """

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Contact first name must not be empty.",
            )

        return normalized

    @field_validator(
        "last_name",
        "phone",
        "job_title",
        "department",
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
        """
        Strip whitespace and convert empty values to None.
        """

        if value is None:
            return None

        normalized = value.strip()

        return normalized or None


class ContactCreate(ContactBase):
    """
    Payload for creating a contact.

    organization_id is intentionally excluded because the
    organization is resolved from the authenticated user.
    """

    pass


class ContactUpdate(BaseModel):
    """
    Partial update payload for a contact.
    """

    company_id: UUID | None = Field(
        default=None,
    )

    first_name: str | None = Field(
        default=None,
        min_length=1,
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

    department: str | None = Field(
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
        "first_name",
        mode="before",
    )
    @classmethod
    def normalize_optional_first_name(
        cls,
        value: str | None,
    ) -> str | None:
        """
        Normalize an optionally supplied first name.
        """

        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Contact first name must not be empty.",
            )

        return normalized

    @field_validator(
        "last_name",
        "phone",
        "job_title",
        "department",
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
        """
        Normalize optional text values.
        """

        if value is None:
            return None

        normalized = value.strip()

        return normalized or None


class ContactResponse(BaseModel):
    """
    Contact API response.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    organization_id: UUID

    company_id: UUID | None

    first_name: str

    last_name: str | None

    email: EmailStr | None

    phone: str | None

    job_title: str | None

    department: str | None

    description: str | None

    address_line_1: str | None

    address_line_2: str | None

    city: str | None

    state: str | None

    postal_code: str | None

    country: str | None

    created_at: datetime

    updated_at: datetime


class ContactListResponse(BaseModel):
    """
    Paginated contact list response.
    """

    items: list[ContactResponse]

    total: int

    limit: int

    offset: int


__all__ = [
    "ContactCreate",
    "ContactListResponse",
    "ContactResponse",
    "ContactUpdate",
]