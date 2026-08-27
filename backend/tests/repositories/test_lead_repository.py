"""
==========================================================
NIVAG AI Business Automation

Lead Repository Tests

Integration tests for tenant-scoped CRM lead persistence.

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
from app.models.lead import Lead, LeadStatus
from app.models.organization import Organization
from app.repositories.lead_repository import LeadRepository


@pytest.mark.asyncio
async def test_create_lead(
    db_session,
) -> None:
    """
    A lead can be created for an organization.
    """

    organization = Organization(
        name="Acme Organization",
        slug=f"acme-{uuid4().hex}",
    )

    db_session.add(
        organization,
    )

    await db_session.flush()

    repository = LeadRepository(
        db_session,
    )

    lead = Lead(
        organization_id=organization.id,
        title="John Doe Lead",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        status=LeadStatus.NEW,
        source="manual",
    )

    created = await repository.create(
        lead,
    )

    assert created.id is not None
    assert created.organization_id == organization.id
    assert created.title == "John Doe Lead"
    assert created.first_name == "John"
    assert created.last_name == "Doe"
    assert created.email == "john@example.com"
    assert created.source == "manual"


@pytest.mark.asyncio
async def test_get_lead_by_id_within_organization(
    db_session,
) -> None:
    """
    A lead can be retrieved within its organization.
    """

    organization = Organization(
        name="Acme Organization",
        slug=f"acme-{uuid4().hex}",
    )

    db_session.add(
        organization,
    )

    await db_session.flush()

    lead = Lead(
        organization_id=organization.id,
        title="John Lead",
        first_name="John",
        email="john@example.com",
    )

    db_session.add(
        lead,
    )

    await db_session.flush()

    repository = LeadRepository(
        db_session,
    )

    result = await repository.get_by_id(
        lead_id=lead.id,
        organization_id=organization.id,
    )

    assert result is not None
    assert result.id == lead.id
    assert result.organization_id == organization.id
    assert result.title == "John Lead"


@pytest.mark.asyncio
async def test_get_lead_returns_none_for_wrong_organization(
    db_session,
) -> None:
    """
    A lead must not be visible from another organization.
    """

    organization = Organization(
        name="Acme Organization",
        slug=f"acme-{uuid4().hex}",
    )

    other_organization = Organization(
        name="Other Organization",
        slug=f"other-{uuid4().hex}",
    )

    db_session.add_all(
        [
            organization,
            other_organization,
        ],
    )

    await db_session.flush()

    lead = Lead(
        organization_id=organization.id,
        title="John Lead",
        first_name="John",
    )

    db_session.add(
        lead,
    )

    await db_session.flush()

    repository = LeadRepository(
        db_session,
    )

    result = await repository.get_by_id(
        lead_id=lead.id,
        organization_id=other_organization.id,
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_lead_returns_none_for_unknown_id(
    db_session,
) -> None:
    """
    Unknown lead IDs return None.
    """

    organization = Organization(
        name="Acme Organization",
        slug=f"acme-{uuid4().hex}",
    )

    db_session.add(
        organization,
    )

    await db_session.flush()

    repository = LeadRepository(
        db_session,
    )

    result = await repository.get_by_id(
        lead_id=uuid4(),
        organization_id=organization.id,
    )

    assert result is None


@pytest.mark.asyncio
async def test_list_leads_is_scoped_to_organization(
    db_session,
) -> None:
    """
    Listing leads returns only records from the requested
    organization.
    """

    organization = Organization(
        name="Acme Organization",
        slug=f"acme-{uuid4().hex}",
    )

    other_organization = Organization(
        name="Other Organization",
        slug=f"other-{uuid4().hex}",
    )

    db_session.add_all(
        [
            organization,
            other_organization,
        ],
    )

    await db_session.flush()

    own_lead = Lead(
        organization_id=organization.id,
        title="Own Lead",
        first_name="John",
    )

    other_lead = Lead(
        organization_id=other_organization.id,
        title="Other Lead",
        first_name="Jane",
    )

    db_session.add_all(
        [
            own_lead,
            other_lead,
        ],
    )

    await db_session.flush()

    repository = LeadRepository(
        db_session,
    )

    leads = await repository.list(
        organization_id=organization.id,
        limit=50,
        offset=0,
    )

    assert len(leads) == 1
    assert leads[0].id == own_lead.id
    assert leads[0].organization_id == organization.id


@pytest.mark.asyncio
async def test_list_leads_supports_pagination(
    db_session,
) -> None:
    """
    Lead listing supports limit and offset pagination.
    """

    organization = Organization(
        name="Acme Organization",
        slug=f"acme-{uuid4().hex}",
    )

    db_session.add(
        organization,
    )

    await db_session.flush()

    leads = [
        Lead(
            organization_id=organization.id,
            title=f"Lead {index}",
            first_name=f"Lead {index}",
        )
        for index in range(5)
    ]

    db_session.add_all(
        leads,
    )

    await db_session.flush()

    repository = LeadRepository(
        db_session,
    )

    first_page = await repository.list(
        organization_id=organization.id,
        limit=2,
        offset=0,
    )

    second_page = await repository.list(
        organization_id=organization.id,
        limit=2,
        offset=2,
    )

    assert len(first_page) == 2
    assert len(second_page) == 2

    first_page_ids = {
        lead.id
        for lead in first_page
    }

    second_page_ids = {
        lead.id
        for lead in second_page
    }

    assert first_page_ids.isdisjoint(
        second_page_ids,
    )


@pytest.mark.asyncio
async def test_count_leads_is_scoped_to_organization(
    db_session,
) -> None:
    """
    Lead count includes only records belonging to the
    requested organization.
    """

    organization = Organization(
        name="Acme Organization",
        slug=f"acme-{uuid4().hex}",
    )

    other_organization = Organization(
        name="Other Organization",
        slug=f"other-{uuid4().hex}",
    )

    db_session.add_all(
        [
            organization,
            other_organization,
        ],
    )

    await db_session.flush()

    db_session.add_all(
        [
            Lead(
                organization_id=organization.id,
                title="John Lead",
                first_name="John",
            ),
            Lead(
                organization_id=organization.id,
                title="Jane Lead",
                first_name="Jane",
            ),
            Lead(
                organization_id=other_organization.id,
                title="Other Lead",
                first_name="Other",
            ),
        ],
    )

    await db_session.flush()

    repository = LeadRepository(
        db_session,
    )

    total = await repository.count(
        organization_id=organization.id,
    )

    assert total == 2


@pytest.mark.asyncio
async def test_update_lead(
    db_session,
) -> None:
    """
    Repository persists lead updates.
    """

    organization = Organization(
        name="Acme Organization",
        slug=f"acme-{uuid4().hex}",
    )

    db_session.add(
        organization,
    )

    await db_session.flush()

    lead = Lead(
        organization_id=organization.id,
        title="John Lead",
        first_name="John",
        status=LeadStatus.NEW,
    )

    db_session.add(
        lead,
    )

    await db_session.flush()

    repository = LeadRepository(
        db_session,
    )

    lead.first_name = "Updated John"
    lead.status = LeadStatus.QUALIFIED

    updated = await repository.update(
        lead,
    )

    assert updated.first_name == "Updated John"
    assert updated.status == LeadStatus.QUALIFIED


@pytest.mark.asyncio
async def test_delete_lead(
    db_session,
) -> None:
    """
    Repository deletes a lead.
    """

    organization = Organization(
        name="Acme Organization",
        slug=f"acme-{uuid4().hex}",
    )

    db_session.add(
        organization,
    )

    await db_session.flush()

    lead = Lead(
        organization_id=organization.id,
        title="John Lead",
        first_name="John",
    )

    db_session.add(
        lead,
    )

    await db_session.flush()

    lead_id = lead.id

    repository = LeadRepository(
        db_session,
    )

    await repository.delete(
        lead,
    )

    result = await repository.get_by_id(
        lead_id=lead_id,
        organization_id=organization.id,
    )

    assert result is None


@pytest.mark.asyncio
async def test_lead_can_be_associated_with_company(
    db_session,
) -> None:
    """
    A lead may be associated with a company.
    """

    organization = Organization(
        name="Acme Organization",
        slug=f"acme-{uuid4().hex}",
    )

    db_session.add(
        organization,
    )

    await db_session.flush()

    company = Company(
        organization_id=organization.id,
        name="Acme Company",
    )

    db_session.add(
        company,
    )

    await db_session.flush()

    lead = Lead(
        organization_id=organization.id,
        company_id=company.id,
        title="Company Lead",
        first_name="John",
    )

    db_session.add(
        lead,
    )

    await db_session.flush()

    repository = LeadRepository(
        db_session,
    )

    result = await repository.get_by_id(
        lead_id=lead.id,
        organization_id=organization.id,
    )

    assert result is not None
    assert result.company_id == company.id


@pytest.mark.asyncio
async def test_lead_can_be_associated_with_contact(
    db_session,
) -> None:
    """
    A lead may be associated with a contact.
    """

    organization = Organization(
        name="Acme Organization",
        slug=f"acme-{uuid4().hex}",
    )

    db_session.add(
        organization,
    )

    await db_session.flush()

    contact = Contact(
        organization_id=organization.id,
        first_name="John",
    )

    db_session.add(
        contact,
    )

    await db_session.flush()

    lead = Lead(
        organization_id=organization.id,
        contact_id=contact.id,
        title="Potential Customer Lead",
        first_name="Potential Customer",
    )

    db_session.add(
        lead,
    )

    await db_session.flush()

    repository = LeadRepository(
        db_session,
    )

    result = await repository.get_by_id(
        lead_id=lead.id,
        organization_id=organization.id,
    )

    assert result is not None
    assert result.contact_id == contact.id