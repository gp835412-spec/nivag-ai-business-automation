"""
==========================================================
NIVAG AI Business Automation

Opportunity API Route Tests

Tests for tenant-scoped CRM opportunity endpoints.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.opportunities import (
    get_opportunity_service,
    router,
)
from app.models.opportunity import (
    Opportunity,
    OpportunityStage,
)
from app.services.opportunity_service import (
    OpportunityNotFoundError,
    OpportunityValidationError,
)


@pytest.fixture
def organization_id():
    """Return a reusable organization ID."""

    return uuid4()


@pytest.fixture
def opportunity(
    organization_id,
):
    """Return a sample opportunity."""

    return Opportunity(
        id=uuid4(),
        organization_id=organization_id,
        name="Enterprise Automation Deal",
        stage=OpportunityStage.PROSPECTING,
        amount=Decimal("250000.00"),
        currency="INR",
        description="Sample opportunity.",
    )


@pytest.fixture
def service():
    """Return a mocked opportunity service."""

    service = AsyncMock()

    service.create_opportunity = AsyncMock()
    service.get_opportunity = AsyncMock()
    service.list_opportunities = AsyncMock()
    service.update_opportunity = AsyncMock()
    service.delete_opportunity = AsyncMock()

    return service


@pytest.fixture
def client(
    service,
):
    """Return a test client with the opportunity service overridden."""

    application = FastAPI()

    application.include_router(
        router,
        prefix="/api/v1",
    )

    application.dependency_overrides[
        get_opportunity_service
    ] = lambda: service

    with TestClient(
        application,
    ) as test_client:
        yield test_client

    application.dependency_overrides.clear()


def test_create_opportunity_returns_created_response(
    client,
    service,
    organization_id,
    opportunity,
):
    """POST should create and return an opportunity."""

    service.create_opportunity.return_value = opportunity

    payload = {
        "name": "Enterprise Automation Deal",
        "stage": "prospecting",
        "amount": "250000.00",
        "currency": "INR",
        "description": "Sample opportunity.",
    }

    response = client.post(
        f"/api/v1/opportunities?organization_id={organization_id}",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["id"] == str(
        opportunity.id,
    )
    assert body["organization_id"] == str(
        organization_id,
    )
    assert body["name"] == "Enterprise Automation Deal"
    assert body["stage"] == "prospecting"

    service.create_opportunity.assert_awaited_once()

    call_kwargs = service.create_opportunity.call_args.kwargs

    assert call_kwargs["organization_id"] == organization_id
    assert call_kwargs["data"].name == payload["name"]
    assert call_kwargs["data"].stage == OpportunityStage.PROSPECTING
    assert call_kwargs["data"].amount == Decimal(
        "250000.00"
    )


def test_create_opportunity_returns_422_for_invalid_reference(
    client,
    service,
    organization_id,
):
    """POST should return 422 for invalid CRM references."""

    service.create_opportunity.side_effect = (
        OpportunityValidationError(
            "Invalid company for this organization."
        )
    )

    payload = {
        "company_id": str(
            uuid4(),
        ),
        "name": "Invalid Opportunity",
        "stage": "prospecting",
    }

    response = client.post(
        f"/api/v1/opportunities?organization_id={organization_id}",
        json=payload,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Invalid company for this organization."
    )

    service.create_opportunity.assert_awaited_once()


def test_create_opportunity_returns_422_for_invalid_payload(
    client,
    service,
    organization_id,
):
    """POST should reject an invalid request payload."""

    payload = {
        "stage": "prospecting",
    }

    response = client.post(
        f"/api/v1/opportunities?organization_id={organization_id}",
        json=payload,
    )

    assert response.status_code == 422

    service.create_opportunity.assert_not_awaited()


def test_list_opportunities_returns_opportunities(
    client,
    service,
    organization_id,
    opportunity,
):
    """GET collection endpoint should return opportunities."""

    service.list_opportunities.return_value = [
        opportunity,
    ]

    response = client.get(
        (
            "/api/v1/opportunities"
            f"?organization_id={organization_id}"
            "&offset=10"
            "&limit=25"
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert len(
        body,
    ) == 1

    assert body[0]["id"] == str(
        opportunity.id,
    )

    service.list_opportunities.assert_awaited_once_with(
        organization_id=organization_id,
        offset=10,
        limit=25,
    )


def test_list_opportunities_uses_default_pagination(
    client,
    service,
    organization_id,
):
    """GET collection endpoint should apply default pagination."""

    service.list_opportunities.return_value = []

    response = client.get(
        f"/api/v1/opportunities"
        f"?organization_id={organization_id}",
    )

    assert response.status_code == 200
    assert response.json() == []

    service.list_opportunities.assert_awaited_once_with(
        organization_id=organization_id,
        offset=0,
        limit=100,
    )


def test_list_opportunities_rejects_invalid_offset(
    client,
    service,
    organization_id,
):
    """GET collection endpoint should reject a negative offset."""

    response = client.get(
        (
            "/api/v1/opportunities"
            f"?organization_id={organization_id}"
            "&offset=-1"
        ),
    )

    assert response.status_code == 422

    service.list_opportunities.assert_not_awaited()


def test_list_opportunities_rejects_invalid_limit(
    client,
    service,
    organization_id,
):
    """GET collection endpoint should reject an invalid limit."""

    response = client.get(
        (
            "/api/v1/opportunities"
            f"?organization_id={organization_id}"
            "&limit=101"
        ),
    )

    assert response.status_code == 422

    service.list_opportunities.assert_not_awaited()


def test_get_opportunity_returns_existing_opportunity(
    client,
    service,
    organization_id,
    opportunity,
):
    """GET detail endpoint should return an existing opportunity."""

    service.get_opportunity.return_value = opportunity

    response = client.get(
        (
            f"/api/v1/opportunities/{opportunity.id}"
            f"?organization_id={organization_id}"
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(
        opportunity.id,
    )
    assert body["organization_id"] == str(
        organization_id,
    )
    assert body["name"] == opportunity.name

    service.get_opportunity.assert_awaited_once_with(
        organization_id=organization_id,
        opportunity_id=opportunity.id,
    )


def test_get_opportunity_returns_404_when_missing(
    client,
    service,
    organization_id,
):
    """GET detail endpoint should return 404 when missing."""

    opportunity_id = uuid4()

    service.get_opportunity.side_effect = (
        OpportunityNotFoundError(
            "Opportunity not found."
        )
    )

    response = client.get(
        (
            f"/api/v1/opportunities/{opportunity_id}"
            f"?organization_id={organization_id}"
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Opportunity not found."
    )


def test_update_opportunity_returns_updated_opportunity(
    client,
    service,
    organization_id,
    opportunity,
):
    """PATCH should update and return an opportunity."""

    opportunity.name = "Updated Opportunity"
    opportunity.amount = Decimal(
        "500000.00"
    )

    service.update_opportunity.return_value = opportunity

    payload = {
        "name": "Updated Opportunity",
        "amount": "500000.00",
    }

    response = client.patch(
        (
            f"/api/v1/opportunities/{opportunity.id}"
            f"?organization_id={organization_id}"
        ),
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "Updated Opportunity"

    service.update_opportunity.assert_awaited_once()

    call_kwargs = service.update_opportunity.call_args.kwargs

    assert call_kwargs["organization_id"] == organization_id
    assert call_kwargs["opportunity_id"] == opportunity.id
    assert call_kwargs["data"].name == (
        "Updated Opportunity"
    )
    assert call_kwargs["data"].amount == Decimal(
        "500000.00"
    )


def test_update_opportunity_returns_404_when_missing(
    client,
    service,
    organization_id,
):
    """PATCH should return 404 for a missing opportunity."""

    opportunity_id = uuid4()

    service.update_opportunity.side_effect = (
        OpportunityNotFoundError(
            "Opportunity not found."
        )
    )

    response = client.patch(
        (
            f"/api/v1/opportunities/{opportunity_id}"
            f"?organization_id={organization_id}"
        ),
        json={
            "name": "Updated Opportunity",
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Opportunity not found."
    )


def test_update_opportunity_returns_422_for_invalid_reference(
    client,
    service,
    organization_id,
):
    """PATCH should return 422 for an invalid CRM reference."""

    opportunity_id = uuid4()

    service.update_opportunity.side_effect = (
        OpportunityValidationError(
            "Invalid contact for this organization."
        )
    )

    response = client.patch(
        (
            f"/api/v1/opportunities/{opportunity_id}"
            f"?organization_id={organization_id}"
        ),
        json={
            "contact_id": str(
                uuid4(),
            ),
        },
    )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "Invalid contact for this organization."
    )


def test_delete_opportunity_returns_204(
    client,
    service,
    organization_id,
):
    """DELETE should remove an existing opportunity."""

    opportunity_id = uuid4()

    response = client.delete(
        (
            f"/api/v1/opportunities/{opportunity_id}"
            f"?organization_id={organization_id}"
        ),
    )

    assert response.status_code == 204
    assert response.content == b""

    service.delete_opportunity.assert_awaited_once_with(
        organization_id=organization_id,
        opportunity_id=opportunity_id,
    )


def test_delete_opportunity_returns_404_when_missing(
    client,
    service,
    organization_id,
):
    """DELETE should return 404 for a missing opportunity."""

    opportunity_id = uuid4()

    service.delete_opportunity.side_effect = (
        OpportunityNotFoundError(
            "Opportunity not found."
        )
    )

    response = client.delete(
        (
            f"/api/v1/opportunities/{opportunity_id}"
            f"?organization_id={organization_id}"
        ),
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Opportunity not found."
    )