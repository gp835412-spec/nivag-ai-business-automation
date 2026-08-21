"""
NIVAG AI Business Automation

User Repository Tests

Integration tests for UserRepository against PostgreSQL.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository


async def create_organization(
    db_session: AsyncSession,
) -> Organization:
    """
    Create a real organization for foreign-key dependent user tests.
    """

    organization = Organization(
        name=f"NIVAG User Test Organization {uuid4().hex}",
        slug=f"nivag-user-test-{uuid4().hex}",
        email=f"{uuid4().hex}@example.com",
    )

    db_session.add(organization)
    await db_session.flush()

    return organization


def build_user(
    organization_id,
    *,
    email: str,
    first_name: str = "Test",
) -> User:
    """
    Build a User entity without persisting it.
    """

    return User(
        organization_id=organization_id,
        email=email,
        password_hash="test-password-hash",
        first_name=first_name,
        last_name="User",
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE,
        is_email_verified=False,
    )


@pytest.mark.asyncio
async def test_add_and_get_by_id(
    db_session: AsyncSession,
) -> None:
    repository = UserRepository(db_session)

    organization = await create_organization(db_session)

    user = build_user(
        organization.id,
        email=f"{uuid4().hex}@example.com",
    )

    created = await repository.add(user)

    assert created.id is not None
    assert created.organization_id == organization.id

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.email == created.email


@pytest.mark.asyncio
async def test_get_by_organization_and_email(
    db_session: AsyncSession,
) -> None:
    repository = UserRepository(db_session)

    organization = await create_organization(db_session)

    email = f"{uuid4().hex}@example.com"

    user = build_user(
        organization.id,
        email=email,
    )

    await repository.add(user)

    fetched = await repository.get_by_organization_and_email(
        organization.id,
        email,
    )

    assert fetched is not None
    assert fetched.id == user.id


@pytest.mark.asyncio
async def test_get_by_organization_and_email_returns_none_for_other_organization(
    db_session: AsyncSession,
) -> None:
    repository = UserRepository(db_session)

    organization = await create_organization(db_session)
    other_organization = await create_organization(db_session)

    email = f"{uuid4().hex}@example.com"

    user = build_user(
        organization.id,
        email=email,
    )

    await repository.add(user)

    fetched = await repository.get_by_organization_and_email(
        other_organization.id,
        email,
    )

    assert fetched is None


@pytest.mark.asyncio
async def test_get_by_email_returns_matching_users(
    db_session: AsyncSession,
) -> None:
    repository = UserRepository(db_session)

    first_organization = await create_organization(db_session)
    second_organization = await create_organization(db_session)

    email = f"{uuid4().hex}@example.com"

    first_user = build_user(
        first_organization.id,
        email=email,
        first_name="First",
    )

    second_user = build_user(
        second_organization.id,
        email=email,
        first_name="Second",
    )

    await repository.add(first_user)
    await repository.add(second_user)

    result = await repository.get_by_email(email)

    assert len(result) == 2
    assert {user.id for user in result} == {
        first_user.id,
        second_user.id,
    }


@pytest.mark.asyncio
async def test_get_by_email_returns_empty_list_when_missing(
    db_session: AsyncSession,
) -> None:
    repository = UserRepository(db_session)

    result = await repository.get_by_email(
        f"{uuid4().hex}@example.com",
    )

    assert result == []


@pytest.mark.asyncio
async def test_list_by_organization(
    db_session: AsyncSession,
) -> None:
    repository = UserRepository(db_session)

    organization = await create_organization(db_session)
    other_organization = await create_organization(db_session)

    first_user = build_user(
        organization.id,
        email=f"{uuid4().hex}@example.com",
    )

    second_user = build_user(
        organization.id,
        email=f"{uuid4().hex}@example.com",
    )

    other_user = build_user(
        other_organization.id,
        email=f"{uuid4().hex}@example.com",
    )

    await repository.add(first_user)
    await repository.add(second_user)
    await repository.add(other_user)

    result = await repository.list_by_organization(
        organization.id,
    )

    assert len(result) == 2

    assert {user.id for user in result} == {
        first_user.id,
        second_user.id,
    }


@pytest.mark.asyncio
async def test_list_by_organization_pagination(
    db_session: AsyncSession,
) -> None:
    repository = UserRepository(db_session)

    organization = await create_organization(db_session)

    users = [
        build_user(
            organization.id,
            email=f"{uuid4().hex}@example.com",
            first_name=f"User {index}",
        )
        for index in range(3)
    ]

    for user in users:
        await repository.add(user)

    result = await repository.list_by_organization(
        organization.id,
        offset=1,
        limit=1,
    )

    assert len(result) == 1

    expected_users = sorted(
       users,
       key=lambda user: (user.created_at, user.id),
    )

    assert result[0].id == expected_users[1].id


@pytest.mark.asyncio
async def test_list_by_organization_rejects_negative_offset(
    db_session: AsyncSession,
) -> None:
    repository = UserRepository(db_session)

    organization = await create_organization(db_session)

    with pytest.raises(
        ValueError,
        match="offset must be greater than or equal to zero",
    ):
        await repository.list_by_organization(
            organization.id,
            offset=-1,
        )


@pytest.mark.asyncio
async def test_list_by_organization_rejects_invalid_limit(
    db_session: AsyncSession,
) -> None:
    repository = UserRepository(db_session)

    organization = await create_organization(db_session)

    with pytest.raises(
        ValueError,
        match="limit must be between 1 and 1000",
    ):
        await repository.list_by_organization(
            organization.id,
            limit=0,
        )

    with pytest.raises(
        ValueError,
        match="limit must be between 1 and 1000",
    ):
        await repository.list_by_organization(
            organization.id,
            limit=1001,
        )


@pytest.mark.asyncio
async def test_update(
    db_session: AsyncSession,
) -> None:
    repository = UserRepository(db_session)

    organization = await create_organization(db_session)

    user = build_user(
        organization.id,
        email=f"{uuid4().hex}@example.com",
    )

    await repository.add(user)

    user.first_name = "Updated"

    updated = await repository.update(user)

    assert updated is user
    assert updated.first_name == "Updated"

    fetched = await repository.get_by_id(user.id)

    assert fetched is not None
    assert fetched.first_name == "Updated"


@pytest.mark.asyncio
async def test_delete(
    db_session: AsyncSession,
) -> None:
    repository = UserRepository(db_session)

    organization = await create_organization(db_session)

    user = build_user(
        organization.id,
        email=f"{uuid4().hex}@example.com",
    )

    await repository.add(user)

    user_id = user.id

    deleted = await repository.delete(user)

    assert deleted is True

    fetched = await repository.get_by_id(user_id)

    assert fetched is None