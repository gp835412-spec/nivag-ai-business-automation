"""
==========================================================
NIVAG AI Business Automation

Contact Repository Tests

Integration tests for tenant-scoped CRM contact persistence.

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
from app.models.organization import Organization
from app.repositories.contact_repository import ContactRepository


async def create_organization(
    db_session,
    *,
    name: str = "Test Organization",
) -> Organization:
    """Create and persist an organization for repository tests."""

    organization = Organization(
        name=name,
        slug=f"test-organization-{uuid4().hex}",
    )

    db_session.add(organization)
    await db_session.flush()

    return organization


async def create_company(
    db_session,
    *,
    organization_id,
    name: str = "Test Company",
) -> Company:
    """Create and persist a company for repository tests."""

    company = Company(
        organization_id=organization_id,
        name=name,
    )

    db_session.add(company)
    await db_session.flush()

    return company


@pytest.mark.asyncio
async def test_create_contact(db_session) -> None:
    organization = await create_organization(db_session)

    repository = ContactRepository(db_session)

    contact = Contact(
        organization_id=organization.id,
        first_name="Anand",
        last_name="Kumar",
        email="anand@example.com",
    )

    created = await repository.create(contact)

    assert created.id is not None
    assert created.organization_id == organization.id
    assert created.first_name == "Anand"
    assert created.last_name == "Kumar"
    assert created.email == "anand@example.com"


@pytest.mark.asyncio
async def test_get_contact_by_id_within_organization(
    db_session,
) -> None:
    organization = await create_organization(db_session)

    repository = ContactRepository(db_session)

    created = await repository.create(
        Contact(
            organization_id=organization.id,
            first_name="Anand",
            email="anand@example.com",
        ),
    )

    result = await repository.get_by_id(
        contact_id=created.id,
        organization_id=organization.id,
    )

    assert result is not None
    assert result.id == created.id
    assert result.organization_id == organization.id


@pytest.mark.asyncio
async def test_get_contact_returns_none_for_wrong_organization(
    db_session,
) -> None:
    first_organization = await create_organization(
        db_session,
        name="First Organization",
    )
    second_organization = await create_organization(
        db_session,
        name="Second Organization",
    )

    repository = ContactRepository(db_session)

    created = await repository.create(
        Contact(
            organization_id=first_organization.id,
            first_name="Anand",
        ),
    )

    result = await repository.get_by_id(
        contact_id=created.id,
        organization_id=second_organization.id,
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_contact_returns_none_for_unknown_id(
    db_session,
) -> None:
    organization = await create_organization(db_session)

    repository = ContactRepository(db_session)

    result = await repository.get_by_id(
        contact_id=uuid4(),
        organization_id=organization.id,
    )

    assert result is None


@pytest.mark.asyncio
async def test_list_contacts_is_scoped_to_organization(
    db_session,
) -> None:
    first_organization = await create_organization(
        db_session,
        name="First Organization",
    )
    second_organization = await create_organization(
        db_session,
        name="Second Organization",
    )

    repository = ContactRepository(db_session)

    await repository.create(
        Contact(
            organization_id=first_organization.id,
            first_name="First",
        ),
    )

    await repository.create(
        Contact(
            organization_id=second_organization.id,
            first_name="Second",
        ),
    )

    contacts = await repository.list(
        organization_id=first_organization.id,
        limit=50,
        offset=0,
    )

    assert len(contacts) == 1
    assert contacts[0].first_name == "First"
    assert contacts[0].organization_id == first_organization.id


@pytest.mark.asyncio
async def test_list_contacts_supports_pagination(
    db_session,
) -> None:
    organization = await create_organization(db_session)

    repository = ContactRepository(db_session)

    for index in range(3):
        await repository.create(
            Contact(
                organization_id=organization.id,
                first_name=f"Contact {index}",
            ),
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
    assert len(second_page) == 1

    first_page_ids = {
        contact.id
        for contact in first_page
    }

    second_page_ids = {
        contact.id
        for contact in second_page
    }

    assert first_page_ids.isdisjoint(second_page_ids)


@pytest.mark.asyncio
async def test_count_contacts_is_scoped_to_organization(
    db_session,
) -> None:
    first_organization = await create_organization(
        db_session,
        name="First Organization",
    )
    second_organization = await create_organization(
        db_session,
        name="Second Organization",
    )

    repository = ContactRepository(db_session)

    await repository.create(
        Contact(
            organization_id=first_organization.id,
            first_name="First One",
        ),
    )

    await repository.create(
        Contact(
            organization_id=first_organization.id,
            first_name="First Two",
        ),
    )

    await repository.create(
        Contact(
            organization_id=second_organization.id,
            first_name="Second One",
        ),
    )

    total = await repository.count(
        organization_id=first_organization.id,
    )

    assert total == 2


@pytest.mark.asyncio
async def test_update_contact(db_session) -> None:
    organization = await create_organization(db_session)

    repository = ContactRepository(db_session)

    contact = await repository.create(
        Contact(
            organization_id=organization.id,
            first_name="Original",
            email="original@example.com",
        ),
    )

    contact.first_name = "Updated"
    contact.email = "updated@example.com"

    updated = await repository.update(contact)

    assert updated.id == contact.id
    assert updated.first_name == "Updated"
    assert updated.email == "updated@example.com"


@pytest.mark.asyncio
async def test_delete_contact(db_session) -> None:
    organization = await create_organization(db_session)

    repository = ContactRepository(db_session)

    contact = await repository.create(
        Contact(
            organization_id=organization.id,
            first_name="Delete Me",
        ),
    )

    await repository.delete(contact)

    result = await repository.get_by_id(
        contact_id=contact.id,
        organization_id=organization.id,
    )

    assert result is None


@pytest.mark.asyncio
async def test_contact_can_be_associated_with_company(
    db_session,
) -> None:
    organization = await create_organization(db_session)

    company = await create_company(
        db_session,
        organization_id=organization.id,
    )

    repository = ContactRepository(db_session)

    created = await repository.create(
        Contact(
            organization_id=organization.id,
            company_id=company.id,
            first_name="Company Contact",
        ),
    )

    result = await repository.get_by_id(
        contact_id=created.id,
        organization_id=organization.id,
    )

    assert result is not None
    assert result.company_id == company.id