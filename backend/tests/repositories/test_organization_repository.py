"""
NIVAG AI Business Automation
Organization Repository Tests

Integration tests for OrganizationRepository against PostgreSQL.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization, OrganizationStatus
from app.repositories.organization_repository import OrganizationRepository


@pytest.mark.asyncio
async def test_add_and_get_by_id(
    db_session: AsyncSession,
) -> None:
    repository = OrganizationRepository(db_session)

    organization = Organization(
        name="NIVAG Test Organization",
        slug=f"nivag-test-{uuid4().hex}",
        legal_name="NIVAG Test Organization Private Limited",
        email="test@example.com",
        phone="+919999999999",
        website="https://example.com",
        description="Repository integration test organization.",
    )

    created = await repository.add(organization)

    assert created.id is not None
    assert created.name == "NIVAG Test Organization"
    assert created.status == OrganizationStatus.ACTIVE

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.slug == created.slug


@pytest.mark.asyncio
async def test_get_by_slug(
    db_session: AsyncSession,
) -> None:
    repository = OrganizationRepository(db_session)

    slug = f"organization-{uuid4().hex}"

    organization = Organization(
        name="Slug Test Organization",
        slug=slug,
    )

    await repository.add(organization)

    fetched = await repository.get_by_slug(slug)

    assert fetched is not None
    assert fetched.id == organization.id
    assert fetched.slug == slug


@pytest.mark.asyncio
async def test_get_by_email(
    db_session: AsyncSession,
) -> None:
    repository = OrganizationRepository(db_session)

    email = f"{uuid4().hex}@example.com"

    organization = Organization(
        name="Email Test Organization",
        slug=f"email-test-{uuid4().hex}",
        email=email,
    )

    await repository.add(organization)

    fetched = await repository.get_by_email(email)

    assert fetched is not None
    assert fetched.id == organization.id
    assert fetched.email == email


@pytest.mark.asyncio
async def test_list_all(
    db_session: AsyncSession,
) -> None:
    repository = OrganizationRepository(db_session)

    first = Organization(
        name="List Test Organization One",
        slug=f"list-one-{uuid4().hex}",
    )

    second = Organization(
        name="List Test Organization Two",
        slug=f"list-two-{uuid4().hex}",
    )

    await repository.add(first)
    await repository.add(second)

    organizations = await repository.list_all()

    organization_ids = {organization.id for organization in organizations}

    assert first.id in organization_ids
    assert second.id in organization_ids


@pytest.mark.asyncio
async def test_delete(
    db_session: AsyncSession,
) -> None:
    repository = OrganizationRepository(db_session)

    organization = Organization(
        name="Delete Test Organization",
        slug=f"delete-test-{uuid4().hex}",
    )

    await repository.add(organization)

    organization_id = organization.id

    deleted = await repository.delete(organization_id)

    assert deleted is True

    fetched = await repository.get_by_id(organization_id)

    assert fetched is None


@pytest.mark.asyncio
async def test_delete_missing_organization(
    db_session: AsyncSession,
) -> None:
    repository = OrganizationRepository(db_session)

    deleted = await repository.delete(uuid4())

    assert deleted is False


@pytest.mark.asyncio
async def test_list_all_rejects_invalid_pagination(
    db_session: AsyncSession,
) -> None:
    repository = OrganizationRepository(db_session)

    with pytest.raises(
        ValueError,
        match="offset must be greater than or equal to zero",
    ):
        await repository.list_all(offset=-1)

    with pytest.raises(
        ValueError,
        match="limit must be between 1 and 1000",
    ):
        await repository.list_all(limit=0)

    with pytest.raises(
        ValueError,
        match="limit must be between 1 and 1000",
    ):
        await repository.list_all(limit=1001)