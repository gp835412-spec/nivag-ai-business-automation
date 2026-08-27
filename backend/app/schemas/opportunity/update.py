"""
==========================================================
NIVAG AI Business Automation

Update Opportunity Schema

Request validation schema for partially updating a
tenant-scoped CRM opportunity.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.opportunity import OpportunityStage


class OpportunityUpdate(BaseModel):
    """
    Request schema for partially updating a CRM opportunity.

    All fields are optional. Fields not provided by the client
    must remain unchanged.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    lead_id: UUID | None = None

    company_id: UUID | None = None

    contact_id: UUID | None = None

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    stage: OpportunityStage | None = None

    amount: Decimal | None = Field(
        default=None,
        max_digits=18,
        decimal_places=2,
        ge=Decimal("0"),
    )

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(
        cls,
        value: str | None,
    ) -> str | None:
        """Ensure a provided opportunity name is not blank."""

        if value is not None and not value:
            raise ValueError(
                "Opportunity name must not be blank.",
            )

        return value

    @field_validator("currency")
    @classmethod
    def normalize_currency(
        cls,
        value: str | None,
    ) -> str | None:
        """Normalize and validate a provided currency code."""

        if value is None:
            return None

        normalized_value = value.upper()

        if not normalized_value.isalpha():
            raise ValueError(
                "Currency must contain only alphabetic characters.",
            )

        return normalized_value


__all__ = [
    "OpportunityUpdate",
]