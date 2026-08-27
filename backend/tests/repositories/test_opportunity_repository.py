"""
==========================================================
NIVAG AI Business Automation

Opportunity Repository Tests

Tests database access behavior for tenant-scoped
CRM opportunities.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.models.company import Company
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.opportunity import Opportunity, OpportunityStage
from app.models.organization import Organization
from app.repositories.opportunity_repository import OpportunityRepository


@pytest.mark.asyncio
async def test_create_opportunity(
    db_session,
) -> None:
    """An opportunity can be persisted through the repository."""

    organization = Organization(
        name="Test Organization",
        slug="test-organization-create-opportunity",
    )

    db_session.add(organization)
    await db_session.flush()

    repository = OpportunityRepository(
        db_session,
    )

    opportunity = Opportunity(
        organization_id=organization.id,
        name="Enterprise Automation Deal",
        stage=OpportunityStage.PROSPECTING,
    )

    created_opportunity = await repository.create(
        opportunity,
    )

    assert created_opportunity.id is not None
    assert created_opportunity.organization_id == organization.id
    assert (
        created_opportunity.name
        == "Enterprise Automation Deal"
    )
    assert (
        created_opportunity.stage
        == OpportunityStage.PROSPECTING
    )


@pytest.mark.asyncio
async def test_get_opportunity_by_id(
    db_session,
) -> None:
    """An opportunity can be retrieved within its organization."""

    organization = Organization(
        name="Test Organization",
        slug="test-organization-get-opportunity",
    )

    db_session.add(organization)
    await db_session.flush()

    opportunity = Opportunity(
        organization_id=organization.id,
        name="CRM Implementation",
    )

    db_session.add(opportunity)
    await db_session.flush()

    repository = OpportunityRepository(
        db_session,
    )

    result = await repository.get_by_id(
        organization_id=organization.id,
        opportunity_id=opportunity.id,
    )

    assert result is not None
    assert result.id == opportunity.id
    assert result.organization_id == organization.id
    assert result.name == "CRM Implementation"


@pytest.mark.asyncio
async def test_get_opportunity_is_tenant_scoped(
    db_session,
) -> None:
    """An opportunity cannot be retrieved from another organization."""

    first_organization = Organization(
        name="First Organization",
        slug="first-organization-opportunity-scope",
    )

    second_organization = Organization(
        name="Second Organization",
        slug="second-organization-opportunity-scope",
    )

    db_session.add_all(
        [
            first_organization,
            second_organization,
        ],
    )

    await db_session.flush()

    opportunity = Opportunity(
        organization_id=first_organization.id,
        name="Private Opportunity",
    )

    db_session.add(opportunity)
    await db_session.flush()

    repository = OpportunityRepository(
        db_session,
    )

    result = await repository.get_by_id(
        organization_id=second_organization.id,
        opportunity_id=opportunity.id,
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_nonexistent_opportunity_returns_none(
    db_session,
) -> None:
    """A nonexistent opportunity returns None."""

    organization = Organization(
        name="Test Organization",
        slug="test-organization-missing-opportunity",
    )

    db_session.add(organization)
    await db_session.flush()

    repository = OpportunityRepository(
        db_session,
    )

    result = await repository.get_by_id(
        organization_id=organization.id,
        opportunity_id=uuid4(),
    )

    assert result is None


@pytest.mark.asyncio
async def test_list_opportunities(
    db_session,
) -> None:
    """Only opportunities belonging to the organization are listed."""

    organization = Organization(
        name="Test Organization",
        slug="test-organization-list-opportunities",
    )

    other_organization = Organization(
        name="Other Organization",
        slug="other-organization-list-opportunities",
    )

    db_session.add_all(
        [
            organization,
            other_organization,
        ],
    )

    await db_session.flush()

    first_opportunity = Opportunity(
        organization_id=organization.id,
        name="First Opportunity",
    )

    second_opportunity = Opportunity(
        organization_id=organization.id,
        name="Second Opportunity",
    )

    other_opportunity = Opportunity(
        organization_id=other_organization.id,
        name="Other Opportunity",
    )

    db_session.add_all(
        [
            first_opportunity,
            second_opportunity,
            other_opportunity,
        ],
    )

    await db_session.flush()

    repository = OpportunityRepository(
        db_session,
    )

    opportunities = await repository.list(
        organization_id=organization.id,
    )

    opportunity_ids = {
        opportunity.id
        for opportunity in opportunities
    }

    assert first_opportunity.id in opportunity_ids
    assert second_opportunity.id in opportunity_ids
    assert other_opportunity.id not in opportunity_ids


@pytest.mark.asyncio
async def test_list_opportunities_supports_pagination(
    db_session,
) -> None:
    """Opportunity listing supports offset and limit."""

    organization = Organization(
        name="Test Organization",
        slug="test-organization-opportunity-pagination",
    )

    db_session.add(organization)
    await db_session.flush()

    opportunities = [
        Opportunity(
            organization_id=organization.id,
            name=f"Opportunity {index}",
        )
        for index in range(5)
    ]

    db_session.add_all(
        opportunities,
    )

    await db_session.flush()

    repository = OpportunityRepository(
        db_session,
    )

    result = await repository.list(
        organization_id=organization.id,
        offset=1,
        limit=2,
    )

    assert len(result) == 2


@pytest.mark.asyncio
async def test_update_opportunity(
    db_session,
) -> None:
    """Changes to an opportunity can be flushed and refreshed."""

    organization = Organization(
        name="Test Organization",
        slug="test-organization-update-opportunity",
    )

    db_session.add(organization)
    await db_session.flush()

    opportunity = Opportunity(
        organization_id=organization.id,
        name="Original Opportunity",
        stage=OpportunityStage.PROSPECTING,
    )

    db_session.add(opportunity)
    await db_session.flush()

    repository = OpportunityRepository(
        db_session,
    )

    opportunity.name = "Updated Opportunity"
    opportunity.stage = OpportunityStage.NEGOTIATION

    updated_opportunity = await repository.update(
        opportunity,
    )

    assert updated_opportunity.id == opportunity.id
    assert updated_opportunity.name == "Updated Opportunity"
    assert (
        updated_opportunity.stage
        == OpportunityStage.NEGOTIATION
    )


@pytest.mark.asyncio
async def test_delete_opportunity(
    db_session,
) -> None:
    """An opportunity can be deleted through the repository."""

    organization = Organization(
        name="Test Organization",
        slug="test-organization-delete-opportunity",
    )

    db_session.add(organization)
    await db_session.flush()

    opportunity = Opportunity(
        organization_id=organization.id,
        name="Opportunity To Delete",
    )

    db_session.add(opportunity)
    await db_session.flush()

    repository = OpportunityRepository(
        db_session,
    )

    opportunity_id = opportunity.id

    await repository.delete(
        opportunity,
    )

    result = await repository.get_by_id(
        organization_id=organization.id,
        opportunity_id=opportunity_id,
    )

    assert result is None


@pytest.mark.asyncio
async def test_opportunity_can_be_associated_with_company(
    db_session,
) -> None:
    """An opportunity can reference a company in the organization."""

    organization = Organization(
        name="Test Organization",
        slug="test-organization-opportunity-company",
    )

    db_session.add(organization)
    await db_session.flush()

    company = Company(
        organization_id=organization.id,
        name="NIVAG Technologies",
    )

    db_session.add(company)
    await db_session.flush()

    opportunity = Opportunity(
        organization_id=organization.id,
        company_id=company.id,
        name="Company Opportunity",
    )

    db_session.add(opportunity)
    await db_session.flush()

    assert opportunity.company_id == company.id


@pytest.mark.asyncio
async def test_opportunity_can_be_associated_with_contact(
    db_session,
) -> None:
    """An opportunity can reference a contact in the organization."""

    organization = Organization(
        name="Test Organization",
        slug="test-organization-opportunity-contact",
    )

    db_session.add(organization)
    await db_session.flush()

    contact = Contact(
        organization_id=organization.id,
        first_name="Anand",
    )

    db_session.add(contact)
    await db_session.flush()

    opportunity = Opportunity(
        organization_id=organization.id,
        contact_id=contact.id,
        name="Contact Opportunity",
    )

    db_session.add(opportunity)
    await db_session.flush()

    assert opportunity.contact_id == contact.id


@pytest.mark.asyncio
async def test_opportunity_can_be_associated_with_lead(
    db_session,
) -> None:
    """An opportunity can reference a lead in the organization."""

    organization = Organization(
        name="Test Organization",
        slug="test-organization-opportunity-lead",
    )

    db_session.add(organization)
    await db_session.flush()

    lead = Lead(
        organization_id=organization.id,
        title="Enterprise Lead",
    )

    db_session.add(lead)
    await db_session.flush()

    opportunity = Opportunity(
        organization_id=organization.id,
        lead_id=lead.id,
        name="Lead Opportunity",
    )

    db_session.add(opportunity)
    await db_session.flush()

    assert opportunity.lead_id == lead.id