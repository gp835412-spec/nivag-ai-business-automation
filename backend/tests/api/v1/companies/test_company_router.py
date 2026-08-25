"""
==========================================================
NIVAG AI Business Automation

Company API Router Tests
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
    organization_name: str = "Company API Test Organization",
) -> tuple[dict, str]:
    """
    Register an organization owner and return registration data
    together with a valid JWT access token.
    """

    organization_slug = unique_slug("company-api")
    email = unique_email("company-owner")
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


def auth_headers(access_token: str) -> dict[str, str]:
    """Return authorization headers for an authenticated request."""

    return {
        "Authorization": f"Bearer {access_token}",
    }


@pytest.mark.asyncio
async def test_create_company() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        response = await client.post(
            "/api/v1/companies",
            headers=auth_headers(access_token),
            json={
                "name": "NIVAG Technologies",
                "email": "contact@nivag.example",
                "phone": "+919999999999",
                "website": "https://nivag.example",
                "industry": "Artificial Intelligence",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["name"] == "NIVAG Technologies"
    assert data["email"] == "contact@nivag.example"
    assert data["phone"] == "+919999999999"
    assert data["website"] == "https://nivag.example/"
    assert data["industry"] == "Artificial Intelligence"


@pytest.mark.asyncio
async def test_create_company_rejects_missing_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/companies",
            json={
                "name": "Unauthorized Company",
            },
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_company_rejects_invalid_payload() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        response = await client.post(
            "/api/v1/companies",
            headers=auth_headers(access_token),
            json={
                "name": "",
            },
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_company_rejects_unknown_fields() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        response = await client.post(
            "/api/v1/companies",
            headers=auth_headers(access_token),
            json={
                "name": "Valid Company",
                "unknown_field": "invalid",
            },
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_company() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        create_response = await client.post(
            "/api/v1/companies",
            headers=auth_headers(access_token),
            json={
                "name": "Lookup Company",
            },
        )

        assert create_response.status_code == 201

        company_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/companies/{company_id}",
            headers=auth_headers(access_token),
        )

    assert response.status_code == 200
    assert response.json()["id"] == company_id
    assert response.json()["name"] == "Lookup Company"


@pytest.mark.asyncio
async def test_get_company_rejects_missing_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            f"/api/v1/companies/{uuid4()}",
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_company_returns_404_for_unknown_company() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        response = await client.get(
            f"/api/v1/companies/{uuid4()}",
            headers=auth_headers(access_token),
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_company_isolated_between_organizations() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, first_token = await register_and_login(
            client,
            organization_name="First Organization",
        )

        _, second_token = await register_and_login(
            client,
            organization_name="Second Organization",
        )

        create_response = await client.post(
            "/api/v1/companies",
            headers=auth_headers(first_token),
            json={
                "name": "Private Company",
            },
        )

        assert create_response.status_code == 201

        company_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/companies/{company_id}",
            headers=auth_headers(second_token),
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_companies() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        for name in (
            "Company One",
            "Company Two",
        ):
            create_response = await client.post(
                "/api/v1/companies",
                headers=auth_headers(access_token),
                json={
                    "name": name,
                },
            )

            assert create_response.status_code == 201

        response = await client.get(
            "/api/v1/companies",
            headers=auth_headers(access_token),
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert len(data["items"]) == 2

    assert {
        company["name"]
        for company in data["items"]
    } == {
        "Company One",
        "Company Two",
    }


@pytest.mark.asyncio
async def test_list_companies_supports_pagination() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        for name in (
            "Company One",
            "Company Two",
            "Company Three",
        ):
            response = await client.post(
                "/api/v1/companies",
                headers=auth_headers(access_token),
                json={
                    "name": name,
                },
            )

            assert response.status_code == 201

        response = await client.get(
            "/api/v1/companies",
            headers=auth_headers(access_token),
            params={
                "limit": 1,
                "offset": 1,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert data["limit"] == 1
    assert data["offset"] == 1
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_list_companies_isolated_between_organizations() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, first_token = await register_and_login(
            client,
            organization_name="First Organization",
        )

        _, second_token = await register_and_login(
            client,
            organization_name="Second Organization",
        )

        first_response = await client.post(
            "/api/v1/companies",
            headers=auth_headers(first_token),
            json={
                "name": "First Organization Company",
            },
        )

        assert first_response.status_code == 201

        second_response = await client.post(
            "/api/v1/companies",
            headers=auth_headers(second_token),
            json={
                "name": "Second Organization Company",
            },
        )

        assert second_response.status_code == 201

        response = await client.get(
            "/api/v1/companies",
            headers=auth_headers(first_token),
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == (
        "First Organization Company"
    )


@pytest.mark.asyncio
async def test_list_companies_rejects_missing_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/companies",
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_company() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        create_response = await client.post(
            "/api/v1/companies",
            headers=auth_headers(access_token),
            json={
                "name": "Original Company",
                "industry": "Software",
            },
        )

        assert create_response.status_code == 201

        company_id = create_response.json()["id"]

        response = await client.patch(
            f"/api/v1/companies/{company_id}",
            headers=auth_headers(access_token),
            json={
                "name": "Updated Company",
                "industry": "Artificial Intelligence",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == company_id
    assert data["name"] == "Updated Company"
    assert data["industry"] == "Artificial Intelligence"


@pytest.mark.asyncio
async def test_update_company_updates_multiple_fields() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        create_response = await client.post(
            "/api/v1/companies",
            headers=auth_headers(access_token),
            json={
                "name": "Original Company",
            },
        )

        assert create_response.status_code == 201

        company_id = create_response.json()["id"]

        response = await client.patch(
            f"/api/v1/companies/{company_id}",
            headers=auth_headers(access_token),
            json={
                "name": "Updated Company",
                "legal_name": (
                    "Updated Company Private Limited"
                ),
                "email": "updated@example.com",
                "phone": "+919999999999",
                "website": "https://updated.example",
                "industry": "Technology",
                "city": "Bengaluru",
                "country": "India",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Company"
    assert data["legal_name"] == (
        "Updated Company Private Limited"
    )
    assert data["email"] == "updated@example.com"
    assert data["phone"] == "+919999999999"
    assert data["website"] == "https://updated.example/"
    assert data["industry"] == "Technology"
    assert data["city"] == "Bengaluru"
    assert data["country"] == "India"


@pytest.mark.asyncio
async def test_update_company_rejects_missing_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.patch(
            f"/api/v1/companies/{uuid4()}",
            json={
                "name": "Unauthorized Update",
            },
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_company_returns_404_for_unknown_company() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        response = await client.patch(
            f"/api/v1/companies/{uuid4()}",
            headers=auth_headers(access_token),
            json={
                "name": "Updated Company",
            },
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_company_rejects_invalid_payload() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        create_response = await client.post(
            "/api/v1/companies",
            headers=auth_headers(access_token),
            json={
                "name": "Valid Company",
            },
        )

        assert create_response.status_code == 201

        company_id = create_response.json()["id"]

        response = await client.patch(
            f"/api/v1/companies/{company_id}",
            headers=auth_headers(access_token),
            json={
                "name": "",
            },
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_company() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        create_response = await client.post(
            "/api/v1/companies",
            headers=auth_headers(access_token),
            json={
                "name": "Delete Company",
            },
        )

        assert create_response.status_code == 201

        company_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/v1/companies/{company_id}",
            headers=auth_headers(access_token),
        )

        get_response = await client.get(
            f"/api/v1/companies/{company_id}",
            headers=auth_headers(access_token),
        )

    assert response.status_code == 204
    assert response.content == b""
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_company_rejects_missing_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.delete(
            f"/api/v1/companies/{uuid4()}",
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_company_returns_404_for_unknown_company() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        response = await client.delete(
            f"/api/v1/companies/{uuid4()}",
            headers=auth_headers(access_token),
        )

    assert response.status_code == 404