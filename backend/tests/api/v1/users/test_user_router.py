"""
==========================================================
NIVAG AI Business Automation

User API Router Tests
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


async def register_owner(
    client: AsyncClient,
    *,
    prefix: str,
) -> tuple[str, str]:
    """
    Register an organization owner and return the organization
    slug together with the owner's access token.
    """

    organization_slug = unique_slug(
        f"{prefix}-organization",
    )
    email = unique_email(
        f"{prefix}-owner",
    )
    password = "TestPassword@2026"

    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": (
                f"{prefix.title()} Organization"
            ),
            "organization_slug": organization_slug,
            "email": email,
            "password": password,
            "first_name": "Owner",
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
        organization_slug,
        login_response.json()["access_token"],
    )


def authorization_headers(
    access_token: str,
) -> dict[str, str]:
    """Return Bearer authorization headers."""

    return {
        "Authorization": f"Bearer {access_token}",
    }


@pytest.mark.asyncio
async def test_create_user() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_owner(
            client,
            prefix="create-user",
        )

        email = unique_email("member")

        response = await client.post(
            "/api/v1/users",
            headers=authorization_headers(
                access_token,
            ),
            json={
                "email": email,
                "password": "MemberPassword@2026",
                "first_name": "Test",
                "last_name": "Member",
                "role": "member",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["email"] == email
    assert data["first_name"] == "Test"
    assert data["last_name"] == "Member"
    assert data["role"] == "member"
    assert data["status"] == "active"
    assert data["is_email_verified"] is False


@pytest.mark.asyncio
async def test_list_users_returns_only_current_organization() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, first_token = await register_owner(
            client,
            prefix="first-list",
        )

        _, second_token = await register_owner(
            client,
            prefix="second-list",
        )

        first_email = unique_email("first-member")
        second_email = unique_email("second-member")

        first_create = await client.post(
            "/api/v1/users",
            headers=authorization_headers(
                first_token,
            ),
            json={
                "email": first_email,
                "password": "MemberPassword@2026",
                "first_name": "First",
            },
        )

        second_create = await client.post(
            "/api/v1/users",
            headers=authorization_headers(
                second_token,
            ),
            json={
                "email": second_email,
                "password": "MemberPassword@2026",
                "first_name": "Second",
            },
        )

        assert first_create.status_code == 201
        assert second_create.status_code == 201

        response = await client.get(
            "/api/v1/users",
            headers=authorization_headers(
                first_token,
            ),
        )

    assert response.status_code == 200

    data = response.json()

    emails = {
        item["email"]
        for item in data["items"]
    }

    assert first_email in emails
    assert second_email not in emails
    assert data["offset"] == 0
    assert data["limit"] == 100


@pytest.mark.asyncio
async def test_get_user() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_owner(
            client,
            prefix="get-user",
        )

        email = unique_email("get-member")

        create_response = await client.post(
            "/api/v1/users",
            headers=authorization_headers(
                access_token,
            ),
            json={
                "email": email,
                "password": "MemberPassword@2026",
                "first_name": "Get",
            },
        )

        assert create_response.status_code == 201

        user_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/users/{user_id}",
            headers=authorization_headers(
                access_token,
            ),
        )

    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["email"] == email


@pytest.mark.asyncio
async def test_update_user() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_owner(
            client,
            prefix="update-user",
        )

        create_response = await client.post(
            "/api/v1/users",
            headers=authorization_headers(
                access_token,
            ),
            json={
                "email": unique_email("update-member"),
                "password": "MemberPassword@2026",
                "first_name": "Original",
            },
        )

        assert create_response.status_code == 201

        user_id = create_response.json()["id"]

        response = await client.patch(
            f"/api/v1/users/{user_id}",
            headers=authorization_headers(
                access_token,
            ),
            json={
                "first_name": "Updated",
                "last_name": "User",
                "phone": "+919999999999",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user_id
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "User"
    assert data["phone"] == "+919999999999"


@pytest.mark.asyncio
async def test_delete_user() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_owner(
            client,
            prefix="delete-user",
        )

        create_response = await client.post(
            "/api/v1/users",
            headers=authorization_headers(
                access_token,
            ),
            json={
                "email": unique_email("delete-member"),
                "password": "MemberPassword@2026",
                "first_name": "Delete",
            },
        )

        assert create_response.status_code == 201

        user_id = create_response.json()["id"]

        delete_response = await client.delete(
            f"/api/v1/users/{user_id}",
            headers=authorization_headers(
                access_token,
            ),
        )

        get_response = await client.get(
            f"/api/v1/users/{user_id}",
            headers=authorization_headers(
                access_token,
            ),
        )

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_member_cannot_create_user() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        organization_slug, owner_token = await register_owner(
            client,
            prefix="member-create",
        )

        member_email = unique_email("restricted-member")
        member_password = "MemberPassword@2026"

        create_member = await client.post(
            "/api/v1/users",
            headers=authorization_headers(
                owner_token,
            ),
            json={
                "email": member_email,
                "password": member_password,
                "first_name": "Restricted",
                "role": "member",
            },
        )

        assert create_member.status_code == 201

        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization_slug": organization_slug,
                "email": member_email,
                "password": member_password,
            },
        )

        assert login_response.status_code == 200

        member_token = login_response.json()[
            "access_token"
        ]

        response = await client.post(
            "/api/v1/users",
            headers=authorization_headers(
                member_token,
            ),
            json={
                "email": unique_email("unauthorized"),
                "password": "MemberPassword@2026",
                "first_name": "Unauthorized",
            },
        )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "You do not have permission to create users."
    )


@pytest.mark.asyncio
async def test_cross_organization_user_access_returns_not_found() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, first_token = await register_owner(
            client,
            prefix="cross-first",
        )

        _, second_token = await register_owner(
            client,
            prefix="cross-second",
        )

        create_response = await client.post(
            "/api/v1/users",
            headers=authorization_headers(
                first_token,
            ),
            json={
                "email": unique_email("cross-member"),
                "password": "MemberPassword@2026",
                "first_name": "Cross",
            },
        )

        assert create_response.status_code == 201

        user_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/users/{user_id}",
            headers=authorization_headers(
                second_token,
            ),
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


@pytest.mark.asyncio
async def test_create_user_rejects_missing_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/users",
            json={
                "email": unique_email("no-token"),
                "password": "MemberPassword@2026",
                "first_name": "NoToken",
            },
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_user_validates_invalid_request() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        _, access_token = await register_owner(
            client,
            prefix="invalid-user",
        )

        response = await client.post(
            "/api/v1/users",
            headers=authorization_headers(
                access_token,
            ),
            json={
                "email": "not-an-email",
                "password": "short",
                "first_name": "",
            },
        )

    assert response.status_code == 422