"""
==========================================================
NIVAG AI Business Automation

Authentication API Router Tests
==========================================================
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def unique_slug(prefix: str) -> str:
    """Return a unique organization slug for integration tests."""

    return f"{prefix}-{uuid4().hex}"


def unique_email(prefix: str) -> str:
    """Return a unique email address for integration tests."""

    return f"{prefix}-{uuid4().hex}@example.com"


@pytest.mark.asyncio
async def test_register_endpoint() -> None:
    organization_slug = unique_slug("api-test")
    email = unique_email("owner-api")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "organization_name": "API Test Organization",
                "organization_slug": organization_slug,
                "email": email,
                "password": "TestPassword@2026",
                "first_name": "Anand",
                "last_name": "Kumar",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["email"] == email
    assert data["first_name"] == "Anand"
    assert data["last_name"] == "Kumar"
    assert data["role"] == "owner"
    assert data["status"] == "active"
    assert data["is_email_verified"] is False


@pytest.mark.asyncio
async def test_register_rejects_duplicate_organization() -> None:
    organization_slug = unique_slug("duplicate-api")
    first_email = unique_email("first-api")
    second_email = unique_email("second-api")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        first_response = await client.post(
            "/api/v1/auth/register",
            json={
                "organization_name": "Duplicate API Organization",
                "organization_slug": organization_slug,
                "email": first_email,
                "password": "TestPassword@2026",
                "first_name": "First",
            },
        )

        second_response = await client.post(
            "/api/v1/auth/register",
            json={
                "organization_name": "Another API Organization",
                "organization_slug": organization_slug,
                "email": second_email,
                "password": "TestPassword@2026",
                "first_name": "Second",
            },
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


@pytest.mark.asyncio
async def test_login_endpoint() -> None:
    organization_slug = unique_slug("login-api")
    email = unique_email("login-api")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "organization_name": "Login API Organization",
                "organization_slug": organization_slug,
                "email": email,
                "password": "TestPassword@2026",
                "first_name": "Login",
            },
        )

        assert register_response.status_code == 201

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization_slug": organization_slug,
                "email": email,
                "password": "TestPassword@2026",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["token_type"] == "bearer"

    assert data["user"]["id"] is not None
    assert data["user"]["email"] == email
    assert data["user"]["role"] == "owner"


@pytest.mark.asyncio
async def test_login_rejects_invalid_password() -> None:
    organization_slug = unique_slug("invalid-login")
    email = unique_email("invalid-login")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "organization_name": "Invalid Login Organization",
                "organization_slug": organization_slug,
                "email": email,
                "password": "TestPassword@2026",
                "first_name": "Invalid",
            },
        )

        assert register_response.status_code == 201

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization_slug": organization_slug,
                "email": email,
                "password": "WrongPassword@2026",
            },
        )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid organization credentials."
    )
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.asyncio
async def test_login_rejects_unknown_organization() -> None:
    organization_slug = unique_slug("unknown-organization")
    email = unique_email("unknown")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization_slug": organization_slug,
                "email": email,
                "password": "TestPassword@2026",
            },
        )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid organization credentials."
    )


@pytest.mark.asyncio
async def test_register_validates_required_fields() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "organization_name": "",
                "organization_slug": "",
                "email": "invalid@example.com",
                "password": "TestPassword@2026",
                "first_name": "",
            },
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_validates_required_fields() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization_slug": "",
                "email": "",
                "password": "",
            },
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_current_user() -> None:
    organization_slug = unique_slug("current-user")
    email = unique_email("current-user")
    password = "TestPassword@2026"

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "organization_name": "Current User Organization",
                "organization_slug": organization_slug,
                "email": email,
                "password": password,
                "first_name": "Current",
                "last_name": "User",
            },
        )

        assert register_response.status_code == 201

        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization_slug": organization_slug,
                "email": email,
                "password": password,
            },
        )

        assert login_response.status_code == 200

        access_token = login_response.json()["access_token"]

        response = await client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] is not None
    assert data["email"] == email
    assert data["first_name"] == "Current"
    assert data["last_name"] == "User"
    assert data["role"] == "owner"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_get_current_user_rejects_missing_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/auth/me",
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_invalid_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": "Bearer invalid-token",
            },
        )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Could not authenticate credentials."
    )

    assert response.headers["www-authenticate"] == "Bearer"