"""
==========================================================
NIVAG AI Business Automation

Company Repository Tests

Tests for tenant-scoped CRM company database operations.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.organization import Organization
from app.repositories.company_repository import CompanyRepository


@pytest.fixture
async def organization(
    db_session: AsyncSession,
) -> Organization:
    organization = Organization(
        name="Test Organization",
        slug="test-organization",
    )

    db_session.add(organization)
    await db_session.commit()
    await db_session.refresh(organization)

    return organization


@pytest.fixture
async def second_organization(
    db_session: AsyncSession,
) -> Organization:
    organization = Organization(
        name="Second Organization",
        slug="second-organization",
    )

    db_session.add(organization)
    await db_session.commit()
    await db_session.refresh(organization)

    return organization


@pytest.fixture
def repository(
    db_session: AsyncSession,
) -> CompanyRepository:
    return CompanyRepository(db_session)


@pytest.mark.asyncio
async def test_create_company(
    repository: CompanyRepository,
    organization: Organization,
) -> None:
    company = await repository.create(
        organization_id=organization.id,
        name="NIVAG Technologies",
        email="contact@nivag.example",
        website="https://nivag.example",
    )

    assert isinstance(company, Company)
    assert company.id is not None
    assert company.organization_id == organization.id
    assert company.name == "NIVAG Technologies"
    assert company.email == "contact@nivag.example"
    assert company.website == "https://nivag.example"


@pytest.mark.asyncio
async def test_get_company_by_id_within_organization(
    repository: CompanyRepository,
    organization: Organization,
) -> None:
    created_company = await repository.create(
        organization_id=organization.id,
        name="NIVAG Technologies",
    )

    company = await repository.get_by_id(
        company_id=created_company.id,
        organization_id=organization.id,
    )

    assert company is not None
    assert company.id == created_company.id
    assert company.organization_id == organization.id


@pytest.mark.asyncio
async def test_get_company_returns_none_for_wrong_organization(
    repository: CompanyRepository,
    organization: Organization,
    second_organization: Organization,
) -> None:
    created_company = await repository.create(
        organization_id=organization.id,
        name="Private Company",
    )

    company = await repository.get_by_id(
        company_id=created_company.id,
        organization_id=second_organization.id,
    )

    assert company is None


@pytest.mark.asyncio
async def test_get_company_returns_none_for_unknown_id(
    repository: CompanyRepository,
    organization: Organization,
) -> None:
    company = await repository.get_by_id(
        company_id=uuid4(),
        organization_id=organization.id,
    )

    assert company is None


@pytest.mark.asyncio
async def test_list_companies_is_scoped_to_organization(
    repository: CompanyRepository,
    organization: Organization,
    second_organization: Organization,
) -> None:
    await repository.create(
        organization_id=organization.id,
        name="Company One",
    )

    await repository.create(
        organization_id=organization.id,
        name="Company Two",
    )

    await repository.create(
        organization_id=second_organization.id,
        name="Other Organization Company",
    )

    companies = await repository.list(
        organization_id=organization.id,
    )

    assert len(companies) == 2
    assert all(
        company.organization_id == organization.id
        for company in companies
    )


@pytest.mark.asyncio
async def test_list_companies_supports_pagination(
    repository: CompanyRepository,
    organization: Organization,
) -> None:
    for index in range(5):
        await repository.create(
            organization_id=organization.id,
            name=f"Company {index}",
        )

    companies = await repository.list(
        organization_id=organization.id,
        limit=2,
        offset=1,
    )

    assert len(companies) == 2


@pytest.mark.asyncio
async def test_count_companies_is_scoped_to_organization(
    repository: CompanyRepository,
    organization: Organization,
    second_organization: Organization,
) -> None:
    await repository.create(
        organization_id=organization.id,
        name="Company One",
    )

    await repository.create(
        organization_id=organization.id,
        name="Company Two",
    )

    await repository.create(
        organization_id=second_organization.id,
        name="Other Company",
    )

    total = await repository.count(
        organization_id=organization.id,
    )

    assert total == 2


@pytest.mark.asyncio
async def test_update_company(
    repository: CompanyRepository,
    organization: Organization,
) -> None:
    company = await repository.create(
        organization_id=organization.id,
        name="Original Name",
    )

    updated_company = await repository.update(
        company,
        name="Updated Name",
        industry="Technology",
    )

    assert updated_company.id == company.id
    assert updated_company.name == "Updated Name"
    assert updated_company.industry == "Technology"


@pytest.mark.asyncio
async def test_delete_company(
    repository: CompanyRepository,
    organization: Organization,
) -> None:
    company = await repository.create(
        organization_id=organization.id,
        name="Company To Delete",
    )

    company_id = company.id

    await repository.delete(company)

    deleted_company = await repository.get_by_id(
        company_id=company_id,
        organization_id=organization.id,
    )

    assert deleted_company is None