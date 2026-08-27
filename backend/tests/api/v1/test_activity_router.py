"""
==========================================================
NIVAG AI Business Automation

Activity API Router Tests

Tests tenant-scoped CRM activity endpoints.

Coverage:
- Create activity
- Create validation errors
- List activities
- Pagination validation
- Get activity
- Update activity
- Delete activity
- Not found handling
- Activity lifecycle validation
- Authenticated organization scoping

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.activities.activity_router import (
    get_activity_service,
    router,
)
from app.models.user import User
from app.security.dependencies import get_current_user
from app.services.activity_service import (
    ActivityNotFoundError,
    ActivityValidationError,
)


class FakeActivityService:
    """
    Test double for ActivityService.

    Records calls and allows individual operations to return
    configured values or raise configured domain exceptions.
    """

    def __init__(
        self,
    ) -> None:
        self.create_result: Any = None
        self.create_error: Exception | None = None

        self.list_result: list[Any] = []
        self.list_error: Exception | None = None

        self.get_result: Any = None
        self.get_error: Exception | None = None

        self.update_result: Any = None
        self.update_error: Exception | None = None

        self.delete_error: Exception | None = None

        self.create_calls: list[dict[str, Any]] = []
        self.list_calls: list[dict[str, Any]] = []
        self.get_calls: list[dict[str, Any]] = []
        self.update_calls: list[dict[str, Any]] = []
        self.delete_calls: list[dict[str, Any]] = []

    async def create_activity(
        self,
        *,
        organization_id: UUID,
        data: Any,
    ) -> Any:
        """
        Record create calls and return or raise configured result.
        """

        self.create_calls.append(
            {
                "organization_id": organization_id,
                "data": data,
            },
        )

        if self.create_error is not None:
            raise self.create_error

        if self.create_result is not None:
            return self.create_result

        return {
            "id": str(uuid4()),
            "organization_id": str(organization_id),
            "activity_type": data.activity_type.value,
            "status": data.status.value,
            "subject": data.subject,
            "description": data.description,
            "due_at": (
                data.due_at.isoformat()
                if data.due_at is not None
                else None
            ),
            "completed_at": (
                data.completed_at.isoformat()
                if data.completed_at is not None
                else None
            ),
        }

    async def list_activities(
        self,
        *,
        organization_id: UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Any]:
        """
        Record list calls and return configured results.
        """

        self.list_calls.append(
            {
                "organization_id": organization_id,
                "offset": offset,
                "limit": limit,
            },
        )

        if self.list_error is not None:
            raise self.list_error

        return self.list_result

    async def get_activity(
        self,
        *,
        organization_id: UUID,
        activity_id: UUID,
    ) -> Any:
        """
        Record get calls and return or raise configured result.
        """

        self.get_calls.append(
            {
                "organization_id": organization_id,
                "activity_id": activity_id,
            },
        )

        if self.get_error is not None:
            raise self.get_error

        if self.get_result is not None:
            return self.get_result

        return {
            "id": str(activity_id),
            "organization_id": str(organization_id),
        }

    async def update_activity(
        self,
        *,
        organization_id: UUID,
        activity_id: UUID,
        data: Any,
    ) -> Any:
        """
        Record update calls and return or raise configured result.
        """

        self.update_calls.append(
            {
                "organization_id": organization_id,
                "activity_id": activity_id,
                "data": data,
            },
        )

        if self.update_error is not None:
            raise self.update_error

        if self.update_result is not None:
            return self.update_result

        return {
            "id": str(activity_id),
            "organization_id": str(organization_id),
        }

    async def delete_activity(
        self,
        *,
        organization_id: UUID,
        activity_id: UUID,
    ) -> None:
        """
        Record delete calls and optionally raise a configured error.
        """

        self.delete_calls.append(
            {
                "organization_id": organization_id,
                "activity_id": activity_id,
            },
        )

        if self.delete_error is not None:
            raise self.delete_error


@pytest.fixture
def organization_id() -> UUID:
    """
    Return the authenticated user's organization ID.
    """

    return uuid4()


@pytest.fixture
def current_user(
    organization_id: UUID,
) -> User:
    """
    Return a minimal authenticated user.

    The activity router only requires organization_id.
    """

    user = User()

    user.organization_id = organization_id

    return user


@pytest.fixture
def fake_service() -> FakeActivityService:
    """
    Return a fresh fake ActivityService.
    """

    return FakeActivityService()


@pytest.fixture
def client(
    current_user: User,
    fake_service: FakeActivityService,
):
    """
    Return a test client with authentication and service
    dependencies overridden.
    """

    application = FastAPI()

    application.include_router(
        router,
        prefix="/api/v1",
    )

    async def override_current_user() -> User:
        return current_user

    def override_activity_service() -> FakeActivityService:
        return fake_service

    application.dependency_overrides[
        get_current_user
    ] = override_current_user

    application.dependency_overrides[
        get_activity_service
    ] = override_activity_service

    with TestClient(
        application,
    ) as test_client:
        yield test_client

    application.dependency_overrides.clear()


def test_create_activity_success(
    client: TestClient,
    fake_service: FakeActivityService,
    organization_id: UUID,
) -> None:
    """
    Creating an activity uses the authenticated user's
    organization ID.
    """

    response = client.post(
        "/api/v1/activities",
        json={
            "activity_type": "task",
            "status": "pending",
            "subject": "Call customer",
        },
    )

    assert response.status_code == 201

    assert len(
        fake_service.create_calls,
    ) == 1

    call = fake_service.create_calls[0]

    assert call["organization_id"] == organization_id

    assert call["data"].subject == "Call customer"


def test_create_activity_validation_error(
    client: TestClient,
    fake_service: FakeActivityService,
) -> None:
    """
    ActivityValidationError maps to HTTP 422.
    """

    fake_service.create_error = ActivityValidationError(
        "Invalid company for this organization.",
    )

    response = client.post(
        "/api/v1/activities",
        json={
            "activity_type": "task",
            "status": "pending",
            "subject": "Call customer",
        },
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": (
            "Invalid company for this organization."
        ),
    }


def test_list_activities_success(
    client: TestClient,
    fake_service: FakeActivityService,
    organization_id: UUID,
) -> None:
    """
    Listing activities uses the authenticated organization.
    """

    fake_service.list_result = []

    response = client.get(
        "/api/v1/activities",
    )

    assert response.status_code == 200

    assert len(
        fake_service.list_calls,
    ) == 1

    assert fake_service.list_calls[0] == {
        "organization_id": organization_id,
        "offset": 0,
        "limit": 100,
    }


def test_list_activities_rejects_negative_offset(
    client: TestClient,
) -> None:
    """
    Negative pagination offsets are rejected by FastAPI.
    """

    response = client.get(
        "/api/v1/activities?offset=-1",
    )

    assert response.status_code == 422


def test_list_activities_rejects_limit_above_maximum(
    client: TestClient,
) -> None:
    """
    Limits above the API maximum are rejected.
    """

    response = client.get(
        "/api/v1/activities?limit=101",
    )

    assert response.status_code == 422


def test_get_activity_success(
    client: TestClient,
    fake_service: FakeActivityService,
    organization_id: UUID,
) -> None:
    """
    Getting an activity uses the authenticated organization.
    """

    activity_id = uuid4()

    response = client.get(
        f"/api/v1/activities/{activity_id}",
    )

    assert response.status_code == 200

    assert len(
        fake_service.get_calls,
    ) == 1

    assert fake_service.get_calls[0] == {
        "organization_id": organization_id,
        "activity_id": activity_id,
    }


def test_get_activity_not_found(
    client: TestClient,
    fake_service: FakeActivityService,
) -> None:
    """
    ActivityNotFoundError maps to HTTP 404.
    """

    fake_service.get_error = ActivityNotFoundError(
        "Activity not found.",
    )

    response = client.get(
        f"/api/v1/activities/{uuid4()}",
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Activity not found.",
    }


def test_update_activity_success(
    client: TestClient,
    fake_service: FakeActivityService,
    organization_id: UUID,
) -> None:
    """
    Updating an activity uses the authenticated organization.
    """

    activity_id = uuid4()

    response = client.patch(
        f"/api/v1/activities/{activity_id}",
        json={
            "subject": "Updated customer call",
        },
    )

    assert response.status_code == 200

    assert len(
        fake_service.update_calls,
    ) == 1

    call = fake_service.update_calls[0]

    assert call["organization_id"] == organization_id

    assert call["activity_id"] == activity_id

    assert (
        call["data"].subject
        == "Updated customer call"
    )


def test_update_activity_not_found(
    client: TestClient,
    fake_service: FakeActivityService,
) -> None:
    """
    Updating a missing activity maps to HTTP 404.
    """

    fake_service.update_error = ActivityNotFoundError(
        "Activity not found.",
    )

    response = client.patch(
        f"/api/v1/activities/{uuid4()}",
        json={
            "subject": "Updated customer call",
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Activity not found.",
    }


def test_update_activity_validation_error(
    client: TestClient,
    fake_service: FakeActivityService,
) -> None:
    """
    ActivityValidationError during update maps to HTTP 422.
    """

    fake_service.update_error = ActivityValidationError(
        "completed_at is required when activity status "
        "is completed.",
    )

    response = client.patch(
        f"/api/v1/activities/{uuid4()}",
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": (
            "completed_at is required when activity status "
            "is completed."
        ),
    }


def test_delete_activity_success(
    client: TestClient,
    fake_service: FakeActivityService,
    organization_id: UUID,
) -> None:
    """
    Deleting an activity returns HTTP 204.
    """

    activity_id = uuid4()

    response = client.delete(
        f"/api/v1/activities/{activity_id}",
    )

    assert response.status_code == 204

    assert response.content == b""

    assert len(
        fake_service.delete_calls,
    ) == 1

    assert fake_service.delete_calls[0] == {
        "organization_id": organization_id,
        "activity_id": activity_id,
    }


def test_delete_activity_not_found(
    client: TestClient,
    fake_service: FakeActivityService,
) -> None:
    """
    Deleting a missing activity maps to HTTP 404.
    """

    fake_service.delete_error = ActivityNotFoundError(
        "Activity not found.",
    )

    response = client.delete(
        f"/api/v1/activities/{uuid4()}",
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Activity not found.",
    }


def test_create_completed_activity_with_timestamp(
    client: TestClient,
    fake_service: FakeActivityService,
) -> None:
    """
    A completed activity request with completed_at
    is accepted and reaches the service.
    """

    completed_at = datetime.now(
        timezone.utc,
    )

    response = client.post(
        "/api/v1/activities",
        json={
            "activity_type": "task",
            "status": "completed",
            "subject": "Completed task",
            "completed_at": completed_at.isoformat(),
        },
    )

    assert response.status_code == 201

    assert len(
        fake_service.create_calls,
    ) == 1

    activity_data = (
        fake_service.create_calls[0]["data"]
    )

    assert (
        activity_data.status.value
        == "completed"
    )

    assert (
        activity_data.completed_at
        is not None
    )