"""
==========================================================
NIVAG AI Business Automation

Lead API Router Tests

Tests for tenant-scoped CRM lead HTTP endpoints.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi import HTTPException
from starlette import status

from app.api.v1.leads.lead_router import (
    create_lead,
    delete_lead,
    get_lead,
    list_leads,
    update_lead,
)
from app.schemas.lead.lead_schema import (
    LeadCreate,
    LeadListResponse,
    LeadResponse,
    LeadStatus,
    LeadUpdate,
)
from app.services.lead_service import (
    LeadCompanyNotFoundError,
    LeadContactNotFoundError,
    LeadNotFoundError,
)


class FakeLeadService:
    """Test double for LeadService."""

    def __init__(self) -> None:
        self.create_result: LeadResponse | None = None
        self.get_result: LeadResponse | None = None
        self.list_result: LeadListResponse | None = None
        self.update_result: LeadResponse | None = None

        self.create_error: Exception | None = None
        self.get_error: Exception | None = None
        self.list_error: Exception | None = None
        self.update_error: Exception | None = None
        self.delete_error: Exception | None = None

        self.create_calls: list[dict[str, object]] = []
        self.get_calls: list[dict[str, object]] = []
        self.list_calls: list[dict[str, object]] = []
        self.update_calls: list[dict[str, object]] = []
        self.delete_calls: list[dict[str, object]] = []

    async def create_lead(
        self,
        *,
        organization_id,
        payload,
    ):
        self.create_calls.append(
            {
                "organization_id": organization_id,
                "payload": payload,
            },
        )

        if self.create_error is not None:
            raise self.create_error

        return self.create_result

    async def get_lead(
        self,
        *,
        lead_id,
        organization_id,
    ):
        self.get_calls.append(
            {
                "lead_id": lead_id,
                "organization_id": organization_id,
            },
        )

        if self.get_error is not None:
            raise self.get_error

        return self.get_result

    async def list_leads(
        self,
        *,
        organization_id,
        limit,
        offset,
    ):
        self.list_calls.append(
            {
                "organization_id": organization_id,
                "limit": limit,
                "offset": offset,
            },
        )

        if self.list_error is not None:
            raise self.list_error

        return self.list_result

    async def update_lead(
        self,
        *,
        lead_id,
        organization_id,
        payload,
    ):
        self.update_calls.append(
            {
                "lead_id": lead_id,
                "organization_id": organization_id,
                "payload": payload,
            },
        )

        if self.update_error is not None:
            raise self.update_error

        return self.update_result

    async def delete_lead(
        self,
        *,
        lead_id,
        organization_id,
    ):
        self.delete_calls.append(
            {
                "lead_id": lead_id,
                "organization_id": organization_id,
            },
        )

        if self.delete_error is not None:
            raise self.delete_error


class FakeCurrentUser:
    """Minimal authenticated user test double."""

    def __init__(
        self,
        organization_id,
    ) -> None:
        self.organization_id = organization_id


@pytest.fixture
def organization_id():
    return uuid4()


@pytest.fixture
def current_user(
    organization_id,
):
    return FakeCurrentUser(
        organization_id,
    )


@pytest.fixture
def lead_response(
    organization_id,
):
    now = datetime.now(
        timezone.utc,
    )

    return LeadResponse(
        id=uuid4(),
        organization_id=organization_id,
        company_id=None,
        contact_id=None,
        title="Enterprise CRM Deal",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+919999999999",
        job_title="Founder",
        company_name="Acme Private Limited",
        source="website",
        status=LeadStatus.NEW,
        estimated_value=Decimal("100000.00"),
        currency="INR",
        description="High-value enterprise opportunity.",
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def service():
    return FakeLeadService()


@pytest.mark.asyncio
async def test_create_lead(
    service,
    current_user,
    organization_id,
    lead_response,
):
    service.create_result = lead_response

    payload = LeadCreate(
        title="Enterprise CRM Deal",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        source="website",
        estimated_value=Decimal("100000.00"),
    )

    result = await create_lead(
        payload=payload,
        current_user=current_user,
        service=service,
    )

    assert result == lead_response
    assert len(
        service.create_calls,
    ) == 1
    assert (
        service.create_calls[0]["organization_id"]
        == organization_id
    )
    assert (
        service.create_calls[0]["payload"]
        == payload
    )


@pytest.mark.asyncio
async def test_list_leads(
    service,
    current_user,
    organization_id,
    lead_response,
):
    service.list_result = LeadListResponse(
        items=[
            lead_response,
        ],
        total=1,
        limit=25,
        offset=0,
    )

    result = await list_leads(
        limit=25,
        offset=0,
        current_user=current_user,
        service=service,
    )

    assert result.total == 1
    assert result.items == [
        lead_response,
    ]

    assert len(
        service.list_calls,
    ) == 1

    assert (
        service.list_calls[0]["organization_id"]
        == organization_id
    )
    assert service.list_calls[0]["limit"] == 25
    assert service.list_calls[0]["offset"] == 0


@pytest.mark.asyncio
async def test_get_lead(
    service,
    current_user,
    organization_id,
    lead_response,
):
    service.get_result = lead_response

    result = await get_lead(
        lead_id=lead_response.id,
        current_user=current_user,
        service=service,
    )

    assert result == lead_response

    assert len(
        service.get_calls,
    ) == 1

    assert (
        service.get_calls[0]["lead_id"]
        == lead_response.id
    )

    assert (
        service.get_calls[0]["organization_id"]
        == organization_id
    )


@pytest.mark.asyncio
async def test_get_lead_returns_404_when_not_found(
    service,
    current_user,
):
    lead_id = uuid4()

    service.get_error = LeadNotFoundError(
        "Lead not found.",
    )

    with pytest.raises(
        HTTPException,
    ) as error_info:
        await get_lead(
            lead_id=lead_id,
            current_user=current_user,
            service=service,
        )

    assert (
        error_info.value.status_code
        == status.HTTP_404_NOT_FOUND
    )

    assert (
        error_info.value.detail
        == "Lead not found."
    )


@pytest.mark.asyncio
async def test_update_lead(
    service,
    current_user,
    organization_id,
    lead_response,
):
    service.update_result = lead_response

    payload = LeadUpdate(
        title="Updated Enterprise Deal",
    )

    result = await update_lead(
        lead_id=lead_response.id,
        payload=payload,
        current_user=current_user,
        service=service,
    )

    assert result == lead_response

    assert len(
        service.update_calls,
    ) == 1

    assert (
        service.update_calls[0]["lead_id"]
        == lead_response.id
    )

    assert (
        service.update_calls[0]["organization_id"]
        == organization_id
    )

    assert (
        service.update_calls[0]["payload"]
        == payload
    )


@pytest.mark.asyncio
async def test_update_lead_returns_404_when_not_found(
    service,
    current_user,
):
    lead_id = uuid4()

    service.update_error = LeadNotFoundError(
        "Lead not found.",
    )

    payload = LeadUpdate(
        title="Updated Lead",
    )

    with pytest.raises(
        HTTPException,
    ) as error_info:
        await update_lead(
            lead_id=lead_id,
            payload=payload,
            current_user=current_user,
            service=service,
        )

    assert (
        error_info.value.status_code
        == status.HTTP_404_NOT_FOUND
    )

    assert (
        error_info.value.detail
        == "Lead not found."
    )


@pytest.mark.asyncio
async def test_update_lead_returns_404_when_company_not_found(
    service,
    current_user,
):
    lead_id = uuid4()
    company_id = uuid4()

    service.update_error = LeadCompanyNotFoundError(
        "Company not found.",
    )

    payload = LeadUpdate(
        company_id=company_id,
    )

    with pytest.raises(
        HTTPException,
    ) as error_info:
        await update_lead(
            lead_id=lead_id,
            payload=payload,
            current_user=current_user,
            service=service,
        )

    assert (
        error_info.value.status_code
        == status.HTTP_404_NOT_FOUND
    )

    assert (
        error_info.value.detail
        == "Company not found."
    )


@pytest.mark.asyncio
async def test_update_lead_returns_404_when_contact_not_found(
    service,
    current_user,
):
    lead_id = uuid4()
    contact_id = uuid4()

    service.update_error = LeadContactNotFoundError(
        "Contact not found.",
    )

    payload = LeadUpdate(
        contact_id=contact_id,
    )

    with pytest.raises(
        HTTPException,
    ) as error_info:
        await update_lead(
            lead_id=lead_id,
            payload=payload,
            current_user=current_user,
            service=service,
        )

    assert (
        error_info.value.status_code
        == status.HTTP_404_NOT_FOUND
    )

    assert (
        error_info.value.detail
        == "Contact not found."
    )


@pytest.mark.asyncio
async def test_delete_lead(
    service,
    current_user,
    organization_id,
):
    lead_id = uuid4()

    response = await delete_lead(
        lead_id=lead_id,
        current_user=current_user,
        service=service,
    )

    assert (
        response.status_code
        == status.HTTP_204_NO_CONTENT
    )

    assert len(
        service.delete_calls,
    ) == 1

    assert (
        service.delete_calls[0]["lead_id"]
        == lead_id
    )

    assert (
        service.delete_calls[0]["organization_id"]
        == organization_id
    )


@pytest.mark.asyncio
async def test_delete_lead_returns_404_when_not_found(
    service,
    current_user,
):
    lead_id = uuid4()

    service.delete_error = LeadNotFoundError(
        "Lead not found.",
    )

    with pytest.raises(
        HTTPException,
    ) as error_info:
        await delete_lead(
            lead_id=lead_id,
            current_user=current_user,
            service=service,
        )

    assert (
        error_info.value.status_code
        == status.HTTP_404_NOT_FOUND
    )

    assert (
        error_info.value.detail
        == "Lead not found."
    )