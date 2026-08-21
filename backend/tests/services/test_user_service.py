"""
NIVAG AI Business Automation

User Service Tests
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User, UserRole, UserStatus
from app.services.user_service import UserService
from app.security.password import verify_password


async def create_organization(
    db_session: AsyncSession,
) -> Organization:
    organization = Organization(
        name=f"User Service Organization {uuid4().hex}",
        slug=f"user-service-{uuid4().hex}",
        email=f"{uuid4().hex}@example.com",
    )

    db_session.add(organization)
    await db_session.flush()

    return organization


@pytest.mark.asyncio
async def test_create_user(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)
    organization = await create_organization(db_session)

    user = await service.create(
        organization_id=organization.id,
        email=" OWNER@EXAMPLE.COM ",
        password="TestPassword@2026",
        first_name=" Anand ",
        last_name=" Kumar ",
    )

    assert user.id is not None
    assert user.organization_id == organization.id
    assert user.email == "owner@example.com"
    assert user.first_name == "Anand"
    assert user.last_name == "Kumar"
    assert user.role == UserRole.MEMBER
    assert user.status == UserStatus.ACTIVE
    assert user.is_email_verified is False
    assert user.password_hash != "TestPassword@2026"
    assert verify_password(
        "TestPassword@2026",
        user.password_hash,
    )


@pytest.mark.asyncio
async def test_create_rejects_duplicate_email(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)
    organization = await create_organization(db_session)

    await service.create(
        organization_id=organization.id,
        email="duplicate@example.com",
        password="TestPassword@2026",
        first_name="First",
    )

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        await service.create(
            organization_id=organization.id,
            email="DUPLICATE@example.com",
            password="AnotherPassword@2026",
            first_name="Second",
        )


@pytest.mark.asyncio
async def test_same_email_allowed_in_different_organizations(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)

    first_organization = await create_organization(db_session)
    second_organization = await create_organization(db_session)

    first_user = await service.create(
        organization_id=first_organization.id,
        email="shared@example.com",
        password="TestPassword@2026",
        first_name="First",
    )

    second_user = await service.create(
        organization_id=second_organization.id,
        email="SHARED@example.com",
        password="TestPassword@2026",
        first_name="Second",
    )

    assert first_user.id != second_user.id
    assert first_user.organization_id != second_user.organization_id
    assert first_user.email == second_user.email


@pytest.mark.asyncio
async def test_get_by_id(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)
    organization = await create_organization(db_session)

    created = await service.create(
        organization_id=organization.id,
        email="get-id@example.com",
        password="TestPassword@2026",
        first_name="Test",
    )

    fetched = await service.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.email == created.email


@pytest.mark.asyncio
async def test_get_by_organization_and_email(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)
    organization = await create_organization(db_session)

    created = await service.create(
        organization_id=organization.id,
        email="lookup@example.com",
        password="TestPassword@2026",
        first_name="Test",
    )

    fetched = await service.get_by_organization_and_email(
        organization.id,
        "LOOKUP@example.com",
    )

    assert fetched is not None
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_get_by_email(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)

    first_organization = await create_organization(db_session)
    second_organization = await create_organization(db_session)

    await service.create(
        organization_id=first_organization.id,
        email="global@example.com",
        password="TestPassword@2026",
        first_name="First",
    )

    await service.create(
        organization_id=second_organization.id,
        email="GLOBAL@example.com",
        password="TestPassword@2026",
        first_name="Second",
    )

    users = await service.get_by_email(
        "global@example.com",
    )

    assert len(users) == 2


@pytest.mark.asyncio
async def test_list_by_organization(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)

    organization = await create_organization(db_session)
    other_organization = await create_organization(db_session)

    first = await service.create(
        organization_id=organization.id,
        email="first@example.com",
        password="TestPassword@2026",
        first_name="First",
    )

    second = await service.create(
        organization_id=organization.id,
        email="second@example.com",
        password="TestPassword@2026",
        first_name="Second",
    )

    await service.create(
        organization_id=other_organization.id,
        email="other@example.com",
        password="TestPassword@2026",
        first_name="Other",
    )

    users = await service.list_by_organization(
        organization.id,
    )

    assert len(users) == 2
    assert {user.id for user in users} == {
        first.id,
        second.id,
    }


@pytest.mark.asyncio
async def test_update_user(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)
    organization = await create_organization(db_session)

    user = await service.create(
        organization_id=organization.id,
        email="update@example.com",
        password="TestPassword@2026",
        first_name="Old",
        last_name="Name",
    )

    updated = await service.update(
        user,
        first_name=" New ",
        last_name=" User ",
        phone=" +919999999999 ",
        role=UserRole.ADMIN,
        status=UserStatus.INACTIVE,
        is_email_verified=True,
    )

    assert updated.first_name == "New"
    assert updated.last_name == "User"
    assert updated.phone == "+919999999999"
    assert updated.role == UserRole.ADMIN
    assert updated.status == UserStatus.INACTIVE
    assert updated.is_email_verified is True


@pytest.mark.asyncio
async def test_update_email(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)
    organization = await create_organization(db_session)

    user = await service.create(
        organization_id=organization.id,
        email="old@example.com",
        password="TestPassword@2026",
        first_name="Test",
    )

    updated = await service.update(
        user,
        email=" NEW@EXAMPLE.COM ",
    )

    assert updated.email == "new@example.com"


@pytest.mark.asyncio
async def test_update_rejects_duplicate_email(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)
    organization = await create_organization(db_session)

    first = await service.create(
        organization_id=organization.id,
        email="first@example.com",
        password="TestPassword@2026",
        first_name="First",
    )

    second = await service.create(
        organization_id=organization.id,
        email="second@example.com",
        password="TestPassword@2026",
        first_name="Second",
    )

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        await service.update(
            second,
            email=first.email,
        )


@pytest.mark.asyncio
async def test_delete_user(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)
    organization = await create_organization(db_session)

    user = await service.create(
        organization_id=organization.id,
        email="delete@example.com",
        password="TestPassword@2026",
        first_name="Delete",
    )

    deleted = await service.delete(user)

    assert deleted is True

    fetched = await service.get_by_id(user.id)

    assert fetched is None


@pytest.mark.asyncio
async def test_delete_missing_user_returns_false(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)

    organization = await create_organization(db_session)

    user = await service.create(
        organization_id=organization.id,
        email=f"{uuid4().hex}@example.com",
        password="TestPassword@2026",
        first_name="Temporary",
    )

    deleted = await service.delete(user)

    assert deleted is True

    deleted_again = await service.delete(user)

    assert deleted_again is False


@pytest.mark.asyncio
async def test_create_rejects_empty_email(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)
    organization = await create_organization(db_session)

    with pytest.raises(
        ValueError,
        match="email must not be empty",
    ):
        await service.create(
            organization_id=organization.id,
            email="   ",
            password="TestPassword@2026",
            first_name="Test",
        )


@pytest.mark.asyncio
async def test_create_rejects_empty_first_name(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)
    organization = await create_organization(db_session)

    with pytest.raises(
        ValueError,
        match="first_name must not be empty",
    ):
        await service.create(
            organization_id=organization.id,
            email="valid@example.com",
            password="TestPassword@2026",
            first_name="   ",
        )


@pytest.mark.asyncio
async def test_create_normalizes_optional_fields(
    db_session: AsyncSession,
) -> None:
    service = UserService(db_session)
    organization = await create_organization(db_session)

    user = await service.create(
        organization_id=organization.id,
        email="optional@example.com",
        password="TestPassword@2026",
        first_name="Test",
        last_name="   ",
        phone="   ",
    )

    assert user.last_name is None
    assert user.phone is None