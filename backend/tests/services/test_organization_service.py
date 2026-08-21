"""
==========================================================
NIVAG AI Business Automation

Organization Service Tests

Production integration tests for OrganizationService.
==========================================================
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.models.organization import Organization
from app.services.organization_service import OrganizationService


@pytest.mark.asyncio
async def test_create_organization(db_session):
    service = OrganizationService(db_session)

    organization = await service.create(
        name="NIVAG Technologies",
        slug="nivag-technologies",
        email="admin@nivag.example",
    )

    assert organization.id is not None
    assert organization.name == "NIVAG Technologies"
    assert organization.slug == "nivag-technologies"
    assert organization.email == "admin@nivag.example"
    assert organization.currency == "INR"
    assert organization.timezone == "Asia/Kolkata"


@pytest.mark.asyncio
async def test_create_normalizes_slug_and_email(db_session):
    service = OrganizationService(db_session)

    organization = await service.create(
        name="NIVAG",
        slug="  NIVAG-INDIA  ",
        email="  ADMIN@NIVAG.EXAMPLE  ",
    )

    assert organization.slug == "nivag-india"
    assert organization.email == "admin@nivag.example"


@pytest.mark.asyncio
async def test_create_rejects_duplicate_slug(db_session):
    service = OrganizationService(db_session)

    await service.create(
        name="First Organization",
        slug="duplicate-slug",
        email="first@example.com",
    )

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        await service.create(
            name="Second Organization",
            slug="duplicate-slug",
            email="second@example.com",
        )


@pytest.mark.asyncio
async def test_create_rejects_duplicate_email(db_session):
    service = OrganizationService(db_session)

    await service.create(
        name="First Organization",
        slug="first-organization",
        email="duplicate@example.com",
    )

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        await service.create(
            name="Second Organization",
            slug="second-organization",
            email="duplicate@example.com",
        )


@pytest.mark.asyncio
async def test_get_by_id(db_session):
    service = OrganizationService(db_session)

    created = await service.create(
        name="Lookup Organization",
        slug="lookup-organization",
        email="lookup@example.com",
    )

    result = await service.get_by_id(created.id)

    assert result is not None
    assert result.id == created.id
    assert result.name == "Lookup Organization"


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_missing_organization(
    db_session,
):
    service = OrganizationService(db_session)

    result = await service.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_get_by_slug(db_session):
    service = OrganizationService(db_session)

    created = await service.create(
        name="Slug Organization",
        slug="slug-organization",
        email="slug@example.com",
    )

    result = await service.get_by_slug(
        "  SLUG-ORGANIZATION  ",
    )

    assert result is not None
    assert result.id == created.id


@pytest.mark.asyncio
async def test_get_by_email(db_session):
    service = OrganizationService(db_session)

    created = await service.create(
        name="Email Organization",
        slug="email-organization",
        email="contact@example.com",
    )

    result = await service.get_by_email(
        "  CONTACT@EXAMPLE.COM  ",
    )

    assert result is not None
    assert result.id == created.id


@pytest.mark.asyncio
async def test_list_all(db_session):
    service = OrganizationService(db_session)

    await service.create(
        name="Organization One",
        slug="organization-one",
        email="one@example.com",
    )

    await service.create(
        name="Organization Two",
        slug="organization-two",
        email="two@example.com",
    )

    organizations = await service.list_all()

    assert len(organizations) == 2
    assert {
        organization.slug
        for organization in organizations
    } == {
        "organization-one",
        "organization-two",
    }


@pytest.mark.asyncio
async def test_update_organization(db_session):
    service = OrganizationService(db_session)

    organization = await service.create(
        name="Original Organization",
        slug="original-organization",
        email="original@example.com",
    )

    organization.name = "Updated Organization"
    organization.slug = "updated-organization"
    organization.email = "updated@example.com"
    organization.currency = "usd"

    updated = await service.update(organization)

    assert updated.name == "Updated Organization"
    assert updated.slug == "updated-organization"
    assert updated.email == "updated@example.com"
    assert updated.currency == "USD"


@pytest.mark.asyncio
async def test_delete_organization(db_session):
    service = OrganizationService(db_session)

    organization = await service.create(
        name="Delete Organization",
        slug="delete-organization",
        email="delete@example.com",
    )

    deleted = await service.delete(organization.id)

    assert deleted is True

    result = await service.get_by_id(organization.id)

    assert result is None


@pytest.mark.asyncio
async def test_delete_missing_organization(db_session):
    service = OrganizationService(db_session)

    deleted = await service.delete(uuid4())

    assert deleted is False


@pytest.mark.asyncio
async def test_create_rejects_empty_name(db_session):
    service = OrganizationService(db_session)

    with pytest.raises(
        ValueError,
        match="name cannot be empty",
    ):
        await service.create(
            name="   ",
            slug="valid-slug",
        )


@pytest.mark.asyncio
async def test_create_rejects_empty_slug(db_session):
    service = OrganizationService(db_session)

    with pytest.raises(
        ValueError,
        match="slug cannot be empty",
    ):
        await service.create(
            name="Valid Organization",
            slug="   ",
        )


@pytest.mark.asyncio
async def test_create_rejects_invalid_currency(db_session):
    service = OrganizationService(db_session)

    with pytest.raises(
        ValueError,
        match="exactly 3 characters",
    ):
        await service.create(
            name="Currency Organization",
            slug="currency-organization",
            currency="IN",
        )


@pytest.mark.asyncio
async def test_list_all_rejects_invalid_pagination(db_session):
    service = OrganizationService(db_session)

    with pytest.raises(
        ValueError,
        match="offset",
    ):
        await service.list_all(offset=-1)

    with pytest.raises(
        ValueError,
        match="limit",
    ):
        await service.list_all(limit=0)

    with pytest.raises(
        ValueError,
        match="limit",
    ):
        await service.list_all(limit=1001)


@pytest.mark.asyncio
async def test_update_rejects_duplicate_slug(db_session):
    service = OrganizationService(db_session)

    first = await service.create(
        name="First Organization",
        slug="first-organization",
        email="first@example.com",
    )

    second = await service.create(
        name="Second Organization",
        slug="second-organization",
        email="second@example.com",
    )

    second.slug = first.slug

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        await service.update(second)


@pytest.mark.asyncio
async def test_update_rejects_duplicate_email(db_session):
    service = OrganizationService(db_session)

    first = await service.create(
        name="First Email Organization",
        slug="first-email-organization",
        email="first-email@example.com",
    )

    second = await service.create(
        name="Second Email Organization",
        slug="second-email-organization",
        email="second-email@example.com",
    )

    second.email = first.email

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        await service.update(second)