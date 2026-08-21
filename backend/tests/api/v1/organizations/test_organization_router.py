"""
==========================================================
NIVAG AI Business Automation

Organization API Router Tests
==========================================================
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def unique_slug(prefix: str) -> str:
    """Return a unique organization slug for API tests."""

    return f"{prefix}-{uuid4().hex}"


def unique_email(prefix: str) -> str:
    """Return a unique email address for API tests."""

    return f"{prefix}-{uuid4().hex}@example.com"


async def register_and_login(
    client: AsyncClient,
    *,
    organization_name: str = "Organization API Test",
) -> tuple[dict, str]:
    """
    Register an organization owner and return the registration
    response data together with a valid JWT access token.
    """

    organization_slug = unique_slug("organization-api")
    email = unique_email("organization-owner")
    password = "TestPassword@2026"

    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": organization_name,
            "organization_slug": organization_slug,
            "email": email,
            "password": password,
            "first_name": "Anand",
            "last_name": "Kumar",
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

    return (
        register_response.json(),
        login_response.json()["access_token"],
    )


@pytest.mark.asyncio
async def test_get_current_organization() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(
            client,
            organization_name="My Organization",
        )

        response = await client.get(
            "/api/v1/organizations/me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] is not None
    assert data["name"] == "My Organization"


@pytest.mark.asyncio
async def test_get_current_organization_rejects_missing_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/organizations/me",
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_organization_rejects_invalid_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/organizations/me",
            headers={
                "Authorization": "Bearer invalid-token",
            },
        )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Could not authenticate credentials."
    )

    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.asyncio
async def test_update_current_organization() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(
            client,
            organization_name="Original Organization",
        )

        response = await client.patch(
            "/api/v1/organizations/me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            json={
                "name": "Updated Organization",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Organization"


@pytest.mark.asyncio
async def test_update_current_organization_updates_multiple_fields() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(
            client,
            organization_name="Original Organization",
        )

        response = await client.patch(
            "/api/v1/organizations/me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            json={
                "name": "Updated Organization",
                "legal_name": "Updated Organization Private Limited",
                "email": "updated@example.com",
                "phone": "+919999999999",
                "timezone": "Asia/Kolkata",
                "currency": "INR",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Organization"
    assert (
        data["legal_name"]
        == "Updated Organization Private Limited"
    )
    assert data["email"] == "updated@example.com"
    assert data["phone"] == "+919999999999"
    assert data["timezone"] == "Asia/Kolkata"
    assert data["currency"] == "INR"


@pytest.mark.asyncio
async def test_update_current_organization_rejects_missing_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.patch(
            "/api/v1/organizations/me",
            json={
                "name": "Unauthorized Update",
            },
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_current_organization_rejects_invalid_payload() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        response = await client.patch(
            "/api/v1/organizations/me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            json={
                "name": "",
            },
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_current_organization_rejects_unknown_fields() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        response = await client.patch(
            "/api/v1/organizations/me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            json={
                "unknown_field": "invalid",
            },
        )

    assert response.status_code == 422