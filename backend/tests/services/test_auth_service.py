"""
NIVAG AI Business Automation

Authentication Service Tests
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import UserRole, UserStatus
from app.security.token import decode_access_token
from app.services.auth import AuthService, AuthenticationError


@pytest.mark.asyncio
async def test_register_creates_organization_and_owner(
    db_session: AsyncSession,
) -> None:
    service = AuthService(db_session)

    user = await service.register(
        organization_name="NIVAG Test Organization",
        organization_slug="nivag-test-organization",
        email="owner@example.com",
        password="TestPassword@2026",
        first_name="Anand",
        last_name="Kumar",
    )

    assert user.id is not None
    assert user.email == "owner@example.com"
    assert user.first_name == "Anand"
    assert user.last_name == "Kumar"
    assert user.role == UserRole.OWNER
    assert user.status == UserStatus.ACTIVE
    assert user.is_email_verified is False

    organization = await db_session.get(
        Organization,
        user.organization_id,
    )

    assert organization is not None
    assert organization.name == "NIVAG Test Organization"
    assert organization.slug == "nivag-test-organization"


@pytest.mark.asyncio
async def test_register_normalizes_email_and_slug(
    db_session: AsyncSession,
) -> None:
    service = AuthService(db_session)

    user = await service.register(
        organization_name=" Test Organization ",
        organization_slug="TEST-ORGANIZATION",
        email=" OWNER@EXAMPLE.COM ",
        password="TestPassword@2026",
        first_name=" Anand ",
    )

    assert user.email == "owner@example.com"

    organization = await db_session.get(
        Organization,
        user.organization_id,
    )

    assert organization is not None
    assert organization.slug == "test-organization"
    assert organization.name == "Test Organization"


@pytest.mark.asyncio
async def test_login_returns_access_token(
    db_session: AsyncSession,
) -> None:
    service = AuthService(db_session)

    await service.register(
        organization_name="Login Organization",
        organization_slug="login-organization",
        email="login@example.com",
        password="TestPassword@2026",
        first_name="Login",
    )

    token = await service.login(
        organization_slug="login-organization",
        email="login@example.com",
        password="TestPassword@2026",
    )

    assert token

    payload = decode_access_token(token)

    assert payload["sub"] is not None


@pytest.mark.asyncio
async def test_login_normalizes_credentials(
    db_session: AsyncSession,
) -> None:
    service = AuthService(db_session)

    user = await service.register(
        organization_name="Normalize Login Organization",
        organization_slug="normalize-login",
        email="owner@example.com",
        password="TestPassword@2026",
        first_name="Owner",
    )

    token = await service.login(
        organization_slug="NORMALIZE-LOGIN",
        email=" OWNER@EXAMPLE.COM ",
        password="TestPassword@2026",
    )

    payload = decode_access_token(token)

    assert payload["sub"] == str(user.id)


@pytest.mark.asyncio
async def test_login_rejects_unknown_organization(
    db_session: AsyncSession,
) -> None:
    service = AuthService(db_session)

    with pytest.raises(
        AuthenticationError,
        match="Invalid organization credentials",
    ):
        await service.login(
            organization_slug="does-not-exist",
            email="owner@example.com",
            password="TestPassword@2026",
        )


@pytest.mark.asyncio
async def test_login_rejects_unknown_user(
    db_session: AsyncSession,
) -> None:
    service = AuthService(db_session)

    await service.register(
        organization_name="Unknown User Organization",
        organization_slug="unknown-user-organization",
        email="owner@example.com",
        password="TestPassword@2026",
        first_name="Owner",
    )

    with pytest.raises(
        AuthenticationError,
        match="Invalid organization credentials",
    ):
        await service.login(
            organization_slug="unknown-user-organization",
            email="unknown@example.com",
            password="TestPassword@2026",
        )


@pytest.mark.asyncio
async def test_login_rejects_wrong_password(
    db_session: AsyncSession,
) -> None:
    service = AuthService(db_session)

    await service.register(
        organization_name="Wrong Password Organization",
        organization_slug="wrong-password-organization",
        email="owner@example.com",
        password="TestPassword@2026",
        first_name="Owner",
    )

    with pytest.raises(
        AuthenticationError,
        match="Invalid organization credentials",
    ):
        await service.login(
            organization_slug="wrong-password-organization",
            email="owner@example.com",
            password="WrongPassword@2026",
        )


@pytest.mark.asyncio
async def test_login_rejects_inactive_user(
    db_session: AsyncSession,
) -> None:
    service = AuthService(db_session)

    user = await service.register(
        organization_name="Inactive User Organization",
        organization_slug="inactive-user-organization",
        email="owner@example.com",
        password="TestPassword@2026",
        first_name="Owner",
    )

    user.status = UserStatus.INACTIVE
    await db_session.flush()

    with pytest.raises(
        AuthenticationError,
        match="User account is not active",
    ):
        await service.login(
            organization_slug="inactive-user-organization",
            email="owner@example.com",
            password="TestPassword@2026",
        )


@pytest.mark.asyncio
async def test_login_rejects_suspended_user(
    db_session: AsyncSession,
) -> None:
    service = AuthService(db_session)

    user = await service.register(
        organization_name="Suspended User Organization",
        organization_slug="suspended-user-organization",
        email="owner@example.com",
        password="TestPassword@2026",
        first_name="Owner",
    )

    user.status = UserStatus.SUSPENDED
    await db_session.flush()

    with pytest.raises(
        AuthenticationError,
        match="User account is not active",
    ):
        await service.login(
            organization_slug="suspended-user-organization",
            email="owner@example.com",
            password="TestPassword@2026",
        )


@pytest.mark.asyncio
async def test_authenticate_user_returns_user(
    db_session: AsyncSession,
) -> None:
    service = AuthService(db_session)

    created = await service.register(
        organization_name="Authenticate Organization",
        organization_slug="authenticate-organization",
        email="owner@example.com",
        password="TestPassword@2026",
        first_name="Owner",
    )

    authenticated = await service.authenticate_user(
        organization_slug="authenticate-organization",
        email="owner@example.com",
        password="TestPassword@2026",
    )

    assert authenticated.id == created.id
    assert authenticated.organization_id == created.organization_id
    assert authenticated.email == created.email


@pytest.mark.asyncio
async def test_register_rejects_duplicate_organization_slug(
    db_session: AsyncSession,
) -> None:
    service = AuthService(db_session)

    await service.register(
        organization_name="First Organization",
        organization_slug="duplicate-organization",
        email="first@example.com",
        password="TestPassword@2026",
        first_name="First",
    )

    with pytest.raises(ValueError):
        await service.register(
            organization_name="Second Organization",
            organization_slug="duplicate-organization",
            email="second@example.com",
            password="TestPassword@2026",
            first_name="Second",
        )