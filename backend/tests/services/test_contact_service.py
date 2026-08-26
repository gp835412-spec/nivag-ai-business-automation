"""
==========================================================
NIVAG AI Business Automation

Contact Service Tests

Production integration tests for ContactService.
==========================================================
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.models.company import Company
from app.models.organization import Organization
from app.repositories.company_repository import CompanyRepository
from app.repositories.contact_repository import ContactRepository
from app.schemas.contact.contact_schema import (
    ContactCreate,
    ContactUpdate,
)
from app.services.contact_service import (
    ContactCompanyNotFoundError,
    ContactNotFoundError,
    ContactService,
)


async def create_organization(
    db_session,
    *,
    name: str,
) -> Organization:
    """
    Create an organization for contact service tests.
    """

    organization = Organization(
        name=name,
        slug=f"{name.lower().replace(' ', '-')}-{uuid4().hex}",
    )

    db_session.add(organization)

    await db_session.flush()
    await db_session.refresh(organization)

    return organization


async def create_company(
    db_session,
    *,
    organization_id,
    name: str,
) -> Company:
    """
    Create a company for contact service tests.
    """

    company = Company(
        organization_id=organization_id,
        name=name,
    )

    db_session.add(company)

    await db_session.flush()
    await db_session.refresh(company)

    return company


def build_service(
    db_session,
) -> ContactService:
    """
    Build ContactService with production repositories.
    """

    return ContactService(
        contact_repository=ContactRepository(
            db_session,
        ),
        company_repository=CompanyRepository(
            db_session,
        ),
    )


@pytest.mark.asyncio
async def test_create_contact(
    db_session,
):
    organization = await create_organization(
        db_session,
        name="Contact Organization",
    )

    service = build_service(db_session)

    contact = await service.create_contact(
        organization_id=organization.id,
        payload=ContactCreate(
            first_name="Anand",
            last_name="Kumar",
            email="anand@example.com",
            phone="+919999999999",
            job_title="Founder",
        ),
    )

    assert contact.id is not None
    assert contact.organization_id == organization.id
    assert contact.first_name == "Anand"
    assert contact.last_name == "Kumar"
    assert contact.email == "anand@example.com"
    assert contact.company_id is None


@pytest.mark.asyncio
async def test_create_contact_with_company(
    db_session,
):
    organization = await create_organization(
        db_session,
        name="Company Contact Organization",
    )

    company = await create_company(
        db_session,
        organization_id=organization.id,
        name="NIVAG Technologies",
    )

    service = build_service(db_session)

    contact = await service.create_contact(
        organization_id=organization.id,
        payload=ContactCreate(
            company_id=company.id,
            first_name="Anand",
            last_name="Kumar",
        ),
    )

    assert contact.company_id == company.id
    assert contact.organization_id == organization.id


@pytest.mark.asyncio
async def test_create_contact_rejects_company_from_another_organization(
    db_session,
):
    first_organization = await create_organization(
        db_session,
        name="First Organization",
    )

    second_organization = await create_organization(
        db_session,
        name="Second Organization",
    )

    company = await create_company(
        db_session,
        organization_id=second_organization.id,
        name="Second Organization Company",
    )

    service = build_service(db_session)

    with pytest.raises(
        ContactCompanyNotFoundError,
        match="Company not found",
    ):
        await service.create_contact(
            organization_id=first_organization.id,
            payload=ContactCreate(
                company_id=company.id,
                first_name="Unauthorized",
            ),
        )


@pytest.mark.asyncio
async def test_create_contact_rejects_unknown_company(
    db_session,
):
    organization = await create_organization(
        db_session,
        name="Unknown Company Organization",
    )

    service = build_service(db_session)

    with pytest.raises(
        ContactCompanyNotFoundError,
        match="Company not found",
    ):
        await service.create_contact(
            organization_id=organization.id,
            payload=ContactCreate(
                company_id=uuid4(),
                first_name="Unknown",
            ),
        )


@pytest.mark.asyncio
async def test_get_contact(
    db_session,
):
    organization = await create_organization(
        db_session,
        name="Get Contact Organization",
    )

    service = build_service(db_session)

    created = await service.create_contact(
        organization_id=organization.id,
        payload=ContactCreate(
            first_name="Get",
            last_name="Contact",
        ),
    )

    contact = await service.get_contact(
        contact_id=created.id,
        organization_id=organization.id,
    )

    assert contact.id == created.id
    assert contact.first_name == "Get"


@pytest.mark.asyncio
async def test_get_contact_rejects_wrong_organization(
    db_session,
):
    first_organization = await create_organization(
        db_session,
        name="First Get Organization",
    )

    second_organization = await create_organization(
        db_session,
        name="Second Get Organization",
    )

    service = build_service(db_session)

    created = await service.create_contact(
        organization_id=first_organization.id,
        payload=ContactCreate(
            first_name="Protected",
        ),
    )

    with pytest.raises(
        ContactNotFoundError,
        match="Contact not found",
    ):
        await service.get_contact(
            contact_id=created.id,
            organization_id=second_organization.id,
        )


@pytest.mark.asyncio
async def test_get_contact_rejects_unknown_contact(
    db_session,
):
    organization = await create_organization(
        db_session,
        name="Missing Contact Organization",
    )

    service = build_service(db_session)

    with pytest.raises(
        ContactNotFoundError,
        match="Contact not found",
    ):
        await service.get_contact(
            contact_id=uuid4(),
            organization_id=organization.id,
        )


@pytest.mark.asyncio
async def test_list_contacts_is_scoped_to_organization(
    db_session,
):
    first_organization = await create_organization(
        db_session,
        name="First List Organization",
    )

    second_organization = await create_organization(
        db_session,
        name="Second List Organization",
    )

    service = build_service(db_session)

    await service.create_contact(
        organization_id=first_organization.id,
        payload=ContactCreate(
            first_name="First",
        ),
    )

    await service.create_contact(
        organization_id=second_organization.id,
        payload=ContactCreate(
            first_name="Second",
        ),
    )

    result = await service.list_contacts(
        organization_id=first_organization.id,
    )

    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].first_name == "First"


@pytest.mark.asyncio
async def test_list_contacts_supports_pagination(
    db_session,
):
    organization = await create_organization(
        db_session,
        name="Pagination Organization",
    )

    service = build_service(db_session)

    for index in range(3):
        await service.create_contact(
            organization_id=organization.id,
            payload=ContactCreate(
                first_name=f"Contact {index}",
            ),
        )

    result = await service.list_contacts(
        organization_id=organization.id,
        limit=2,
        offset=1,
    )

    assert result.total == 3
    assert len(result.items) == 2
    assert result.limit == 2
    assert result.offset == 1


@pytest.mark.asyncio
async def test_list_contacts_rejects_invalid_pagination(
    db_session,
):
    organization = await create_organization(
        db_session,
        name="Invalid Pagination Organization",
    )

    service = build_service(db_session)

    with pytest.raises(
        ValueError,
        match="offset",
    ):
        await service.list_contacts(
            organization_id=organization.id,
            offset=-1,
        )

    with pytest.raises(
        ValueError,
        match="limit",
    ):
        await service.list_contacts(
            organization_id=organization.id,
            limit=0,
        )

    with pytest.raises(
        ValueError,
        match="limit",
    ):
        await service.list_contacts(
            organization_id=organization.id,
            limit=101,
        )


@pytest.mark.asyncio
async def test_update_contact(
    db_session,
):
    organization = await create_organization(
        db_session,
        name="Update Contact Organization",
    )

    service = build_service(db_session)

    created = await service.create_contact(
        organization_id=organization.id,
        payload=ContactCreate(
            first_name="Original",
            last_name="Contact",
        ),
    )

    updated = await service.update_contact(
        contact_id=created.id,
        organization_id=organization.id,
        payload=ContactUpdate(
            first_name="Updated",
            job_title="Director",
        ),
    )

    assert updated.first_name == "Updated"
    assert updated.last_name == "Contact"
    assert updated.job_title == "Director"


@pytest.mark.asyncio
async def test_update_contact_assigns_same_organization_company(
    db_session,
):
    organization = await create_organization(
        db_session,
        name="Update Company Organization",
    )

    company = await create_company(
        db_session,
        organization_id=organization.id,
        name="NIVAG Company",
    )

    service = build_service(db_session)

    created = await service.create_contact(
        organization_id=organization.id,
        payload=ContactCreate(
            first_name="Contact",
        ),
    )

    updated = await service.update_contact(
        contact_id=created.id,
        organization_id=organization.id,
        payload=ContactUpdate(
            company_id=company.id,
        ),
    )

    assert updated.company_id == company.id


@pytest.mark.asyncio
async def test_update_contact_rejects_cross_tenant_company(
    db_session,
):
    first_organization = await create_organization(
        db_session,
        name="First Update Organization",
    )

    second_organization = await create_organization(
        db_session,
        name="Second Update Organization",
    )

    company = await create_company(
        db_session,
        organization_id=second_organization.id,
        name="Protected Company",
    )

    service = build_service(db_session)

    created = await service.create_contact(
        organization_id=first_organization.id,
        payload=ContactCreate(
            first_name="Protected Contact",
        ),
    )

    with pytest.raises(
        ContactCompanyNotFoundError,
        match="Company not found",
    ):
        await service.update_contact(
            contact_id=created.id,
            organization_id=first_organization.id,
            payload=ContactUpdate(
                company_id=company.id,
            ),
        )


@pytest.mark.asyncio
async def test_update_contact_rejects_unknown_contact(
    db_session,
):
    organization = await create_organization(
        db_session,
        name="Unknown Update Organization",
    )

    service = build_service(db_session)

    with pytest.raises(
        ContactNotFoundError,
        match="Contact not found",
    ):
        await service.update_contact(
            contact_id=uuid4(),
            organization_id=organization.id,
            payload=ContactUpdate(
                first_name="Updated",
            ),
        )


@pytest.mark.asyncio
async def test_delete_contact(
    db_session,
):
    organization = await create_organization(
        db_session,
        name="Delete Contact Organization",
    )

    service = build_service(db_session)

    created = await service.create_contact(
        organization_id=organization.id,
        payload=ContactCreate(
            first_name="Delete",
        ),
    )

    await service.delete_contact(
        contact_id=created.id,
        organization_id=organization.id,
    )

    with pytest.raises(
        ContactNotFoundError,
        match="Contact not found",
    ):
        await service.get_contact(
            contact_id=created.id,
            organization_id=organization.id,
        )


@pytest.mark.asyncio
async def test_delete_contact_rejects_wrong_organization(
    db_session,
):
    first_organization = await create_organization(
        db_session,
        name="First Delete Organization",
    )

    second_organization = await create_organization(
        db_session,
        name="Second Delete Organization",
    )

    service = build_service(db_session)

    created = await service.create_contact(
        organization_id=first_organization.id,
        payload=ContactCreate(
            first_name="Protected Delete",
        ),
    )

    with pytest.raises(
        ContactNotFoundError,
        match="Contact not found",
    ):
        await service.delete_contact(
            contact_id=created.id,
            organization_id=second_organization.id,
        )


@pytest.mark.asyncio
async def test_delete_contact_rejects_unknown_contact(
    db_session,
):
    organization = await create_organization(
        db_session,
        name="Unknown Delete Organization",
    )

    service = build_service(db_session)

    with pytest.raises(
        ContactNotFoundError,
        match="Contact not found",
    ):
        await service.delete_contact(
            contact_id=uuid4(),
            organization_id=organization.id,
        )