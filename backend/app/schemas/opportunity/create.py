"""
==========================================================
NIVAG AI Business Automation

Create Opportunity Schema

Request validation schema for creating a tenant-scoped
CRM opportunity.

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


class OpportunityCreate(BaseModel):
    """
    Request schema for creating a CRM opportunity.

    The organization_id is intentionally not accepted here.
    It must be resolved from the authenticated tenant context.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    lead_id: UUID | None = None

    company_id: UUID | None = None

    contact_id: UUID | None = None

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    stage: OpportunityStage = OpportunityStage.PROSPECTING

    amount: Decimal | None = Field(
        default=None,
        max_digits=18,
        decimal_places=2,
        ge=Decimal("0"),
    )

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )

    description: str | None = Field(
        default=None,
    )

    @field_validator("name")
    @classmethod
    def validate_name(
        cls,
        value: str,
    ) -> str:
        """Ensure the opportunity name is not blank."""

        if not value:
            raise ValueError(
                "Opportunity name must not be blank.",
            )

        return value

    @field_validator("currency")
    @classmethod
    def normalize_currency(
        cls,
        value: str,
    ) -> str:
        """Normalize and validate the ISO-style currency code."""

        normalized_value = value.upper()

        if not normalized_value.isalpha():
            raise ValueError(
                "Currency must contain only alphabetic characters.",
            )

        return normalized_value


__all__ = [
    "OpportunityCreate",
]