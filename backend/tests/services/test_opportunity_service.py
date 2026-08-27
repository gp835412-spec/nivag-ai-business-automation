"""
==========================================================
NIVAG AI Business Automation

Opportunity Service Tests

Unit tests for tenant-scoped CRM opportunity business logic.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.models.company import Company
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.opportunity import Opportunity, OpportunityStage
from app.repositories.opportunity_repository import OpportunityRepository
from app.schemas.opportunity.create import OpportunityCreate
from app.schemas.opportunity.update import OpportunityUpdate
from app.services.opportunity_service import (
    OpportunityNotFoundError,
    OpportunityService,
    OpportunityValidationError,
)


@pytest.fixture
def organization_id():
    """Return a reusable organization ID."""

    return uuid4()


@pytest.fixture
def repository():
    """Return a mocked opportunity repository."""

    repository = Mock(
        spec=OpportunityRepository,
    )

    repository.create = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.list = AsyncMock()
    repository.update = AsyncMock()
    repository.delete = AsyncMock()

    repository.session = Mock()
    repository.session.get = AsyncMock()

    return repository


@pytest.fixture
def service(
    repository,
):
    """Return the opportunity service under test."""

    return OpportunityService(
        repository=repository,
    )


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


@pytest.mark.asyncio
async def test_create_opportunity_without_references(
    service,
    repository,
    organization_id,
):
    """Creating an opportunity without references should succeed."""

    data = OpportunityCreate(
        name="New Opportunity",
        stage=OpportunityStage.PROSPECTING,
        amount=Decimal("100000.00"),
        currency="INR",
        description="New opportunity.",
    )

    created_opportunity = Opportunity(
        id=uuid4(),
        organization_id=organization_id,
        name=data.name,
        stage=data.stage,
        amount=data.amount,
        currency=data.currency,
        description=data.description,
    )

    repository.create.return_value = created_opportunity

    result = await service.create_opportunity(
        organization_id=organization_id,
        data=data,
    )

    assert result is created_opportunity

    repository.create.assert_awaited_once()

    created_argument = repository.create.call_args.kwargs[
        "opportunity"
    ]

    assert created_argument.organization_id == organization_id
    assert created_argument.name == data.name
    assert created_argument.stage == data.stage
    assert created_argument.amount == data.amount
    assert created_argument.currency == data.currency
    assert created_argument.description == data.description

    repository.session.get.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_opportunity_with_valid_references(
    service,
    repository,
    organization_id,
):
    """Creating an opportunity with same-tenant references should succeed."""

    lead_id = uuid4()
    company_id = uuid4()
    contact_id = uuid4()

    lead = Mock(
        spec=Lead,
    )
    lead.organization_id = organization_id

    company = Mock(
        spec=Company,
    )
    company.organization_id = organization_id

    contact = Mock(
        spec=Contact,
    )
    contact.organization_id = organization_id

    repository.session.get.side_effect = [
        lead,
        company,
        contact,
    ]

    data = OpportunityCreate(
        lead_id=lead_id,
        company_id=company_id,
        contact_id=contact_id,
        name="Referenced Opportunity",
        stage=OpportunityStage.QUALIFICATION,
        amount=Decimal("50000.00"),
        currency="INR",
    )

    created_opportunity = Opportunity(
        id=uuid4(),
        organization_id=organization_id,
        lead_id=lead_id,
        company_id=company_id,
        contact_id=contact_id,
        name=data.name,
        stage=data.stage,
        amount=data.amount,
        currency=data.currency,
    )

    repository.create.return_value = created_opportunity

    result = await service.create_opportunity(
        organization_id=organization_id,
        data=data,
    )

    assert result is created_opportunity

    assert repository.session.get.await_count == 3

    repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_opportunity_rejects_invalid_lead(
    service,
    repository,
    organization_id,
):
    """Creating an opportunity with an invalid lead should fail."""

    lead_id = uuid4()

    repository.session.get.return_value = None

    data = OpportunityCreate(
        lead_id=lead_id,
        name="Invalid Lead Opportunity",
        stage=OpportunityStage.PROSPECTING,
    )

    with pytest.raises(
        OpportunityValidationError,
        match="Invalid lead for this organization.",
    ):
        await service.create_opportunity(
            organization_id=organization_id,
            data=data,
        )

    repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_opportunity_rejects_cross_tenant_company(
    service,
    repository,
    organization_id,
):
    """Creating an opportunity with another tenant's company should fail."""

    company = Mock(
        spec=Company,
    )
    company.organization_id = uuid4()

    repository.session.get.return_value = company

    data = OpportunityCreate(
        company_id=uuid4(),
        name="Invalid Company Opportunity",
        stage=OpportunityStage.PROSPECTING,
    )

    with pytest.raises(
        OpportunityValidationError,
        match="Invalid company for this organization.",
    ):
        await service.create_opportunity(
            organization_id=organization_id,
            data=data,
        )

    repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_opportunity_returns_existing_opportunity(
    service,
    repository,
    organization_id,
    opportunity,
):
    """Getting an existing opportunity should return it."""

    repository.get_by_id.return_value = opportunity

    result = await service.get_opportunity(
        organization_id=organization_id,
        opportunity_id=opportunity.id,
    )

    assert result is opportunity

    repository.get_by_id.assert_awaited_once_with(
        organization_id=organization_id,
        opportunity_id=opportunity.id,
    )


@pytest.mark.asyncio
async def test_get_opportunity_raises_when_not_found(
    service,
    repository,
    organization_id,
):
    """Getting a missing opportunity should raise a domain error."""

    opportunity_id = uuid4()

    repository.get_by_id.return_value = None

    with pytest.raises(
        OpportunityNotFoundError,
        match="Opportunity not found.",
    ):
        await service.get_opportunity(
            organization_id=organization_id,
            opportunity_id=opportunity_id,
        )

    repository.get_by_id.assert_awaited_once_with(
        organization_id=organization_id,
        opportunity_id=opportunity_id,
    )


@pytest.mark.asyncio
async def test_list_opportunities_returns_repository_results(
    service,
    repository,
    organization_id,
):
    """Listing opportunities should delegate to the repository."""

    opportunities = [
        Mock(
            spec=Opportunity,
        ),
        Mock(
            spec=Opportunity,
        ),
    ]

    repository.list.return_value = opportunities

    result = await service.list_opportunities(
        organization_id=organization_id,
        offset=10,
        limit=25,
    )

    assert result == opportunities

    repository.list.assert_awaited_once_with(
        organization_id=organization_id,
        offset=10,
        limit=25,
    )


@pytest.mark.asyncio
async def test_update_opportunity_updates_only_supplied_fields(
    service,
    repository,
    organization_id,
    opportunity,
):
    """Updating should modify only explicitly supplied fields."""

    repository.get_by_id.return_value = opportunity
    repository.update.return_value = opportunity

    data = OpportunityUpdate(
        name="Updated Opportunity",
        amount=Decimal("350000.00"),
    )

    result = await service.update_opportunity(
        organization_id=organization_id,
        opportunity_id=opportunity.id,
        data=data,
    )

    assert result is opportunity
    assert opportunity.name == "Updated Opportunity"
    assert opportunity.amount == Decimal("350000.00")
    assert opportunity.stage == OpportunityStage.PROSPECTING

    repository.update.assert_awaited_once_with(
        opportunity=opportunity,
    )

    repository.session.get.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_opportunity_validates_updated_references(
    service,
    repository,
    organization_id,
    opportunity,
):
    """Updating a CRM reference should validate tenant ownership."""

    company_id = uuid4()

    company = Mock(
        spec=Company,
    )
    company.organization_id = organization_id

    repository.get_by_id.return_value = opportunity
    repository.session.get.return_value = company
    repository.update.return_value = opportunity

    data = OpportunityUpdate(
        company_id=company_id,
    )

    result = await service.update_opportunity(
        organization_id=organization_id,
        opportunity_id=opportunity.id,
        data=data,
    )

    assert result is opportunity
    assert opportunity.company_id == company_id

    repository.session.get.assert_awaited_once_with(
        Company,
        company_id,
    )

    repository.update.assert_awaited_once_with(
        opportunity=opportunity,
    )


@pytest.mark.asyncio
async def test_update_opportunity_rejects_invalid_reference(
    service,
    repository,
    organization_id,
    opportunity,
):
    """Updating to an invalid reference should fail."""

    repository.get_by_id.return_value = opportunity
    repository.session.get.return_value = None

    contact_id = uuid4()

    data = OpportunityUpdate(
        contact_id=contact_id,
    )

    with pytest.raises(
        OpportunityValidationError,
        match="Invalid contact for this organization.",
    ):
        await service.update_opportunity(
            organization_id=organization_id,
            opportunity_id=opportunity.id,
            data=data,
        )

    repository.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_opportunity_raises_when_not_found(
    service,
    repository,
    organization_id,
):
    """Updating a missing opportunity should raise a domain error."""

    opportunity_id = uuid4()

    repository.get_by_id.return_value = None

    data = OpportunityUpdate(
        name="Updated Name",
    )

    with pytest.raises(
        OpportunityNotFoundError,
        match="Opportunity not found.",
    ):
        await service.update_opportunity(
            organization_id=organization_id,
            opportunity_id=opportunity_id,
            data=data,
        )

    repository.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_opportunity_deletes_existing_opportunity(
    service,
    repository,
    organization_id,
    opportunity,
):
    """Deleting an existing opportunity should delegate to repository."""

    repository.get_by_id.return_value = opportunity

    await service.delete_opportunity(
        organization_id=organization_id,
        opportunity_id=opportunity.id,
    )

    repository.get_by_id.assert_awaited_once_with(
        organization_id=organization_id,
        opportunity_id=opportunity.id,
    )

    repository.delete.assert_awaited_once_with(
        opportunity=opportunity,
    )


@pytest.mark.asyncio
async def test_delete_opportunity_raises_when_not_found(
    service,
    repository,
    organization_id,
):
    """Deleting a missing opportunity should raise a domain error."""

    opportunity_id = uuid4()

    repository.get_by_id.return_value = None

    with pytest.raises(
        OpportunityNotFoundError,
        match="Opportunity not found.",
    ):
        await service.delete_opportunity(
            organization_id=organization_id,
            opportunity_id=opportunity_id,
        )

    repository.delete.assert_not_awaited()