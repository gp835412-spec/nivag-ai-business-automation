"""
==========================================================
NIVAG AI Business Automation

Company Service Tests

Production integration tests for CompanyService.
==========================================================
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.models.organization import Organization
from app.repositories.company_repository import CompanyRepository
from app.schemas.company.company_schema import (
    CompanyCreate,
    CompanyUpdate,
)
from app.services.company_service import (
    CompanyNotFoundError,
    CompanyService,
)


async def create_organization(
    db_session,
    *,
    name: str = "NIVAG Technologies",
    slug: str = "nivag-technologies",
) -> Organization:
    organization = Organization(
        name=name,
        slug=slug,
    )

    db_session.add(organization)
    await db_session.flush()
    await db_session.refresh(organization)

    return organization


def create_service(db_session) -> CompanyService:
    return CompanyService(
        CompanyRepository(db_session),
    )


@pytest.mark.asyncio
async def test_create_company(db_session):
    organization = await create_organization(db_session)
    service = create_service(db_session)

    company = await service.create_company(
        organization_id=organization.id,
        payload=CompanyCreate(
            name="Acme Technologies",
            email="contact@acme.example",
            website="https://acme.example",
            industry="Technology",
        ),
    )

    assert company.id is not None
    assert company.organization_id == organization.id
    assert company.name == "Acme Technologies"
    assert company.email == "contact@acme.example"
    assert company.website == "https://acme.example/"


@pytest.mark.asyncio
async def test_create_company_is_scoped_to_organization(db_session):
    first_organization = await create_organization(
        db_session,
        name="First Organization",
        slug="first-organization",
    )
    second_organization = await create_organization(
        db_session,
        name="Second Organization",
        slug="second-organization",
    )

    service = create_service(db_session)

    first_company = await service.create_company(
        organization_id=first_organization.id,
        payload=CompanyCreate(
            name="Shared Name",
        ),
    )

    second_company = await service.create_company(
        organization_id=second_organization.id,
        payload=CompanyCreate(
            name="Shared Name",
        ),
    )

    assert first_company.organization_id == first_organization.id
    assert second_company.organization_id == second_organization.id
    assert first_company.id != second_company.id


@pytest.mark.asyncio
async def test_get_company(db_session):
    organization = await create_organization(db_session)
    service = create_service(db_session)

    created = await service.create_company(
        organization_id=organization.id,
        payload=CompanyCreate(
            name="Lookup Company",
        ),
    )

    result = await service.get_company(
        company_id=created.id,
        organization_id=organization.id,
    )

    assert result.id == created.id
    assert result.name == "Lookup Company"
    assert result.organization_id == organization.id


@pytest.mark.asyncio
async def test_get_company_rejects_wrong_organization(db_session):
    first_organization = await create_organization(
        db_session,
        name="First Organization",
        slug="first-organization",
    )
    second_organization = await create_organization(
        db_session,
        name="Second Organization",
        slug="second-organization",
    )

    service = create_service(db_session)

    company = await service.create_company(
        organization_id=first_organization.id,
        payload=CompanyCreate(
            name="Private Company",
        ),
    )

    with pytest.raises(
        CompanyNotFoundError,
        match="Company not found",
    ):
        await service.get_company(
            company_id=company.id,
            organization_id=second_organization.id,
        )


@pytest.mark.asyncio
async def test_get_company_rejects_unknown_company(db_session):
    organization = await create_organization(db_session)
    service = create_service(db_session)

    with pytest.raises(
        CompanyNotFoundError,
        match="Company not found",
    ):
        await service.get_company(
            company_id=uuid4(),
            organization_id=organization.id,
        )


@pytest.mark.asyncio
async def test_list_companies(db_session):
    organization = await create_organization(db_session)
    service = create_service(db_session)

    await service.create_company(
        organization_id=organization.id,
        payload=CompanyCreate(
            name="Company One",
        ),
    )

    await service.create_company(
        organization_id=organization.id,
        payload=CompanyCreate(
            name="Company Two",
        ),
    )

    result = await service.list_companies(
        organization_id=organization.id,
    )

    assert result.total == 2
    assert result.limit == 50
    assert result.offset == 0
    assert len(result.items) == 2
    assert {
        company.name
        for company in result.items
    } == {
        "Company One",
        "Company Two",
    }


@pytest.mark.asyncio
async def test_list_companies_is_scoped_to_organization(db_session):
    first_organization = await create_organization(
        db_session,
        name="First Organization",
        slug="first-organization",
    )
    second_organization = await create_organization(
        db_session,
        name="Second Organization",
        slug="second-organization",
    )

    service = create_service(db_session)

    await service.create_company(
        organization_id=first_organization.id,
        payload=CompanyCreate(
            name="First Company",
        ),
    )

    await service.create_company(
        organization_id=second_organization.id,
        payload=CompanyCreate(
            name="Second Company",
        ),
    )

    result = await service.list_companies(
        organization_id=first_organization.id,
    )

    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].name == "First Company"


@pytest.mark.asyncio
async def test_list_companies_normalizes_pagination(db_session):
    organization = await create_organization(db_session)
    service = create_service(db_session)

    result = await service.list_companies(
        organization_id=organization.id,
        limit=0,
        offset=-10,
    )

    assert result.limit == 1
    assert result.offset == 0

    result = await service.list_companies(
        organization_id=organization.id,
        limit=500,
    )

    assert result.limit == 100


@pytest.mark.asyncio
async def test_update_company(db_session):
    organization = await create_organization(db_session)
    service = create_service(db_session)

    company = await service.create_company(
        organization_id=organization.id,
        payload=CompanyCreate(
            name="Original Company",
            industry="Software",
        ),
    )

    updated = await service.update_company(
        company_id=company.id,
        organization_id=organization.id,
        payload=CompanyUpdate(
            name="Updated Company",
            industry="Artificial Intelligence",
        ),
    )

    assert updated.id == company.id
    assert updated.name == "Updated Company"
    assert updated.industry == "Artificial Intelligence"


@pytest.mark.asyncio
async def test_update_company_updates_only_provided_fields(db_session):
    organization = await create_organization(db_session)
    service = create_service(db_session)

    company = await service.create_company(
        organization_id=organization.id,
        payload=CompanyCreate(
            name="Original Company",
            email="original@example.com",
            industry="Technology",
        ),
    )

    updated = await service.update_company(
        company_id=company.id,
        organization_id=organization.id,
        payload=CompanyUpdate(
            name="Updated Company",
        ),
    )

    assert updated.name == "Updated Company"
    assert updated.email == "original@example.com"
    assert updated.industry == "Technology"


@pytest.mark.asyncio
async def test_update_company_can_clear_optional_field(db_session):
    organization = await create_organization(db_session)
    service = create_service(db_session)

    company = await service.create_company(
        organization_id=organization.id,
        payload=CompanyCreate(
            name="Clear Field Company",
            phone="+91-9999999999",
        ),
    )

    updated = await service.update_company(
        company_id=company.id,
        organization_id=organization.id,
        payload=CompanyUpdate(
            phone=None,
        ),
    )

    assert updated.phone is None


@pytest.mark.asyncio
async def test_update_company_rejects_wrong_organization(db_session):
    first_organization = await create_organization(
        db_session,
        name="First Organization",
        slug="first-organization",
    )
    second_organization = await create_organization(
        db_session,
        name="Second Organization",
        slug="second-organization",
    )

    service = create_service(db_session)

    company = await service.create_company(
        organization_id=first_organization.id,
        payload=CompanyCreate(
            name="Protected Company",
        ),
    )

    with pytest.raises(
        CompanyNotFoundError,
        match="Company not found",
    ):
        await service.update_company(
            company_id=company.id,
            organization_id=second_organization.id,
            payload=CompanyUpdate(
                name="Unauthorized Update",
            ),
        )


@pytest.mark.asyncio
async def test_delete_company(db_session):
    organization = await create_organization(db_session)
    service = create_service(db_session)

    company = await service.create_company(
        organization_id=organization.id,
        payload=CompanyCreate(
            name="Delete Company",
        ),
    )

    await service.delete_company(
        company_id=company.id,
        organization_id=organization.id,
    )

    with pytest.raises(
        CompanyNotFoundError,
        match="Company not found",
    ):
        await service.get_company(
            company_id=company.id,
            organization_id=organization.id,
        )


@pytest.mark.asyncio
async def test_delete_company_rejects_wrong_organization(db_session):
    first_organization = await create_organization(
        db_session,
        name="First Organization",
        slug="first-organization",
    )
    second_organization = await create_organization(
        db_session,
        name="Second Organization",
        slug="second-organization",
    )

    service = create_service(db_session)

    company = await service.create_company(
        organization_id=first_organization.id,
        payload=CompanyCreate(
            name="Protected Company",
        ),
    )

    with pytest.raises(
        CompanyNotFoundError,
        match="Company not found",
    ):
        await service.delete_company(
            company_id=company.id,
            organization_id=second_organization.id,
        )


@pytest.mark.asyncio
async def test_create_company_normalizes_text_and_website(db_session):
    organization = await create_organization(db_session)
    service = create_service(db_session)

    company = await service.create_company(
        organization_id=organization.id,
        payload=CompanyCreate(
            name="  NIVAG AI  ",
            legal_name="  NIVAG Artificial Intelligence Pvt Ltd  ",
            industry="  Artificial Intelligence  ",
            website="https://nivag.example",
        ),
    )

    assert company.name == "NIVAG AI"
    assert company.legal_name == (
        "NIVAG Artificial Intelligence Pvt Ltd"
    )
    assert company.industry == "Artificial Intelligence"
    assert company.website == "https://nivag.example/"