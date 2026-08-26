"""
==========================================================
NIVAG AI Business Automation

Contact API Router Tests
==========================================================
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def unique_slug(prefix: str) -> str:
    """Return a unique organization slug."""

    return f"{prefix}-{uuid4().hex}"


def unique_email(prefix: str) -> str:
    """Return a unique email address."""

    return f"{prefix}-{uuid4().hex}@example.com"


async def register_and_login(
    client: AsyncClient,
    *,
    organization_name: str = "Contact API Test Organization",
) -> tuple[dict, str]:
    """
    Register an organization owner and return the registration
    response together with a valid JWT access token.
    """

    organization_slug = unique_slug("contact-api")
    email = unique_email("contact-owner")
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
    """Return bearer authentication headers."""

    return {
        "Authorization": f"Bearer {access_token}",
    }


async def create_company(
    client: AsyncClient,
    *,
    access_token: str,
    name: str = "NIVAG Technologies",
) -> dict:
    """Create and return a company for contact tests."""

    response = await client.post(
        "/api/v1/companies",
        headers=auth_headers(access_token),
        json={
            "name": name,
            "email": unique_email("company"),
        },
    )

    assert response.status_code == 201

    return response.json()


async def create_contact(
    client: AsyncClient,
    *,
    access_token: str,
    first_name: str = "Anand",
    email: str | None = None,
    company_id: str | None = None,
) -> dict:
    """Create and return a contact."""

    payload: dict[str, str] = {
        "first_name": first_name,
    }

    if email is not None:
        payload["email"] = email

    if company_id is not None:
        payload["company_id"] = company_id

    response = await client.post(
        "/api/v1/contacts",
        headers=auth_headers(access_token),
        json=payload,
    )

    assert response.status_code == 201

    return response.json()


@pytest.mark.asyncio
async def test_create_contact() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        response = await client.post(
            "/api/v1/contacts",
            headers=auth_headers(access_token),
            json={
                "first_name": "Anand",
                "last_name": "Kumar",
                "email": unique_email("contact"),
                "phone": "+919999999999",
                "job_title": "Founder",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["first_name"] == "Anand"
    assert data["last_name"] == "Kumar"
    assert data["job_title"] == "Founder"
    assert data["company_id"] is None


@pytest.mark.asyncio
async def test_create_contact_with_company() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        company = await create_company(
            client,
            access_token=access_token,
        )

        response = await client.post(
            "/api/v1/contacts",
            headers=auth_headers(access_token),
            json={
                "first_name": "Company",
                "last_name": "Contact",
                "company_id": company["id"],
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["company_id"] == company["id"]


@pytest.mark.asyncio
async def test_create_contact_rejects_foreign_company() -> None:
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

        foreign_company = await create_company(
            client,
            access_token=first_token,
            name="Foreign Company",
        )

        response = await client.post(
            "/api/v1/contacts",
            headers=auth_headers(second_token),
            json={
                "first_name": "Invalid",
                "company_id": foreign_company["id"],
            },
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found."


@pytest.mark.asyncio
async def test_create_contact_rejects_missing_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/contacts",
            json={
                "first_name": "Unauthorized",
            },
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_contacts() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        await create_contact(
            client,
            access_token=access_token,
            first_name="First",
        )

        await create_contact(
            client,
            access_token=access_token,
            first_name="Second",
        )

        response = await client.get(
            "/api/v1/contacts",
            headers=auth_headers(access_token),
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["limit"] == 50
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_list_contacts_is_tenant_scoped() -> None:
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

        await create_contact(
            client,
            access_token=first_token,
            first_name="First Organization Contact",
        )

        response = await client.get(
            "/api/v1/contacts",
            headers=auth_headers(second_token),
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_list_contacts_supports_pagination() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        await create_contact(
            client,
            access_token=access_token,
            first_name="First",
        )

        await create_contact(
            client,
            access_token=access_token,
            first_name="Second",
        )

        response = await client.get(
            "/api/v1/contacts",
            headers=auth_headers(access_token),
            params={
                "limit": 1,
                "offset": 1,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert len(data["items"]) == 1
    assert data["limit"] == 1
    assert data["offset"] == 1


@pytest.mark.asyncio
async def test_get_contact() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        contact = await create_contact(
            client,
            access_token=access_token,
            first_name="Lookup",
        )

        response = await client.get(
            f"/api/v1/contacts/{contact['id']}",
            headers=auth_headers(access_token),
        )

    assert response.status_code == 200
    assert response.json()["id"] == contact["id"]


@pytest.mark.asyncio
async def test_get_contact_rejects_foreign_organization() -> None:
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

        contact = await create_contact(
            client,
            access_token=first_token,
        )

        response = await client.get(
            f"/api/v1/contacts/{contact['id']}",
            headers=auth_headers(second_token),
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found."


@pytest.mark.asyncio
async def test_get_missing_contact_returns_404() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        response = await client.get(
            f"/api/v1/contacts/{uuid4()}",
            headers=auth_headers(access_token),
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found."


@pytest.mark.asyncio
async def test_update_contact() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        contact = await create_contact(
            client,
            access_token=access_token,
            first_name="Original",
        )

        response = await client.patch(
            f"/api/v1/contacts/{contact['id']}",
            headers=auth_headers(access_token),
            json={
                "first_name": "Updated",
                "last_name": "Contact",
                "job_title": "CEO",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Contact"
    assert data["job_title"] == "CEO"


@pytest.mark.asyncio
async def test_update_contact_company() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        contact = await create_contact(
            client,
            access_token=access_token,
        )

        company = await create_company(
            client,
            access_token=access_token,
        )

        response = await client.patch(
            f"/api/v1/contacts/{contact['id']}",
            headers=auth_headers(access_token),
            json={
                "company_id": company["id"],
            },
        )

    assert response.status_code == 200
    assert response.json()["company_id"] == company["id"]


@pytest.mark.asyncio
async def test_update_contact_allows_removing_company() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        company = await create_company(
            client,
            access_token=access_token,
        )

        contact = await create_contact(
            client,
            access_token=access_token,
            company_id=company["id"],
        )

        response = await client.patch(
            f"/api/v1/contacts/{contact['id']}",
            headers=auth_headers(access_token),
            json={
                "company_id": None,
            },
        )

    assert response.status_code == 200
    assert response.json()["company_id"] is None


@pytest.mark.asyncio
async def test_update_contact_rejects_foreign_company() -> None:
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

        contact = await create_contact(
            client,
            access_token=second_token,
        )

        foreign_company = await create_company(
            client,
            access_token=first_token,
        )

        response = await client.patch(
            f"/api/v1/contacts/{contact['id']}",
            headers=auth_headers(second_token),
            json={
                "company_id": foreign_company["id"],
            },
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found."


@pytest.mark.asyncio
async def test_update_missing_contact_returns_404() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        response = await client.patch(
            f"/api/v1/contacts/{uuid4()}",
            headers=auth_headers(access_token),
            json={
                "first_name": "Updated",
            },
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found."


@pytest.mark.asyncio
async def test_delete_contact() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        contact = await create_contact(
            client,
            access_token=access_token,
        )

        response = await client.delete(
            f"/api/v1/contacts/{contact['id']}",
            headers=auth_headers(access_token),
        )

        get_response = await client.get(
            f"/api/v1/contacts/{contact['id']}",
            headers=auth_headers(access_token),
        )

    assert response.status_code == 204
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_contact_rejects_foreign_organization() -> None:
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

        contact = await create_contact(
            client,
            access_token=first_token,
        )

        response = await client.delete(
            f"/api/v1/contacts/{contact['id']}",
            headers=auth_headers(second_token),
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found."


@pytest.mark.asyncio
async def test_delete_missing_contact_returns_404() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_and_login(client)

        response = await client.delete(
            f"/api/v1/contacts/{uuid4()}",
            headers=auth_headers(access_token),
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found."


@pytest.mark.asyncio
async def test_contact_endpoints_reject_missing_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        contact_id = uuid4()

        list_response = await client.get(
            "/api/v1/contacts",
        )

        get_response = await client.get(
            f"/api/v1/contacts/{contact_id}",
        )

        patch_response = await client.patch(
            f"/api/v1/contacts/{contact_id}",
            json={
                "first_name": "Unauthorized",
            },
        )

        delete_response = await client.delete(
            f"/api/v1/contacts/{contact_id}",
        )

    assert list_response.status_code == 401
    assert get_response.status_code == 401
    assert patch_response.status_code == 401
    assert delete_response.status_code == 401