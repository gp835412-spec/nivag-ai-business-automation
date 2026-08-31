"""
==========================================================
NIVAG AI Business Automation

Activity Repository Tests

Tests persistence operations for tenant-scoped CRM
activities.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models.activity import (
    Activity,
    ActivityStatus,
    ActivityType,
)
from app.repositories.activity_repository import (
    ActivityRepository,
)


@pytest.fixture
def session() -> AsyncMock:
    """
    Return a mocked asynchronous database session.

    AsyncSession.add() is synchronous.
    AsyncSession.delete(), execute(), flush(), and refresh()
    are asynchronous methods for this test contract.
    """

    session = AsyncMock()

    session.add = MagicMock()

    return session


@pytest.fixture
def repository(
    session: AsyncMock,
) -> ActivityRepository:
    """
    Return an ActivityRepository configured with the
    mocked database session.
    """

    return ActivityRepository(
        session=session,
    )


@pytest.fixture
def activity() -> Activity:
    """
    Return a valid Activity entity.
    """

    return Activity(
        organization_id=uuid4(),
        activity_type=ActivityType.TASK,
        status=ActivityStatus.PENDING,
        subject="Follow up with customer",
        description="Discuss the proposal.",
        due_at=datetime.now(
            timezone.utc,
        ),
    )


def test_session_property(
    repository: ActivityRepository,
    session: AsyncMock,
) -> None:
    """
    The repository must expose the configured database
    session.
    """

    assert repository.session is session


@pytest.mark.asyncio
async def test_create(
    repository: ActivityRepository,
    session: AsyncMock,
    activity: Activity,
) -> None:
    """
    Creating an activity must add, flush, and refresh the
    entity before returning it.
    """

    result = await repository.create(
        activity=activity,
    )

    assert result is activity

    session.add.assert_called_once_with(
        activity,
    )

    session.flush.assert_awaited_once()

    session.refresh.assert_awaited_once_with(
        activity,
    )


@pytest.mark.asyncio
async def test_get_by_id_returns_activity(
    repository: ActivityRepository,
    session: AsyncMock,
    activity: Activity,
) -> None:
    """
    get_by_id must return the matching tenant-scoped
    activity when it exists.
    """

    organization_id = activity.organization_id
    activity_id = uuid4()

    activity.id = activity_id

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = activity

    session.execute.return_value = result_mock

    result = await repository.get_by_id(
        organization_id=organization_id,
        activity_id=activity_id,
    )

    assert result is activity

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_not_found(
    repository: ActivityRepository,
    session: AsyncMock,
) -> None:
    """
    get_by_id must return None when no matching activity
    exists.
    """

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None

    session.execute.return_value = result_mock

    result = await repository.get_by_id(
        organization_id=uuid4(),
        activity_id=uuid4(),
    )

    assert result is None

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_returns_activities(
    repository: ActivityRepository,
    session: AsyncMock,
) -> None:
    """
    list must return activities belonging to the requested
    organization.
    """

    activities = [
        Activity(
            organization_id=uuid4(),
            activity_type=ActivityType.TASK,
            status=ActivityStatus.PENDING,
            subject="First activity",
        ),
        Activity(
            organization_id=uuid4(),
            activity_type=ActivityType.CALL,
            status=ActivityStatus.COMPLETED,
            subject="Second activity",
        ),
    ]

    organization_id = uuid4()

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = activities

    session.execute.return_value = result_mock

    result = await repository.list(
        organization_id=organization_id,
        offset=0,
        limit=100,
    )

    assert result == activities

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_rejects_negative_offset(
    repository: ActivityRepository,
) -> None:
    """
    list must reject negative offsets.
    """

    with pytest.raises(
        ValueError,
        match="offset must be greater than or equal to zero",
    ):
        await repository.list(
            organization_id=uuid4(),
            offset=-1,
            limit=100,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "limit",
    [
        0,
        -1,
        1001,
    ],
)
async def test_list_rejects_invalid_limit(
    repository: ActivityRepository,
    limit: int,
) -> None:
    """
    list must reject limits outside the supported range.
    """

    with pytest.raises(
        ValueError,
        match="limit must be between 1 and 1000",
    ):
        await repository.list(
            organization_id=uuid4(),
            offset=0,
            limit=limit,
        )


@pytest.mark.asyncio
async def test_update(
    repository: ActivityRepository,
    session: AsyncMock,
    activity: Activity,
) -> None:
    """
    update must flush and refresh the tracked activity.
    """

    activity.subject = "Updated subject"

    result = await repository.update(
        activity=activity,
    )

    assert result is activity

    session.flush.assert_awaited_once()

    session.refresh.assert_awaited_once_with(
        activity,
    )


@pytest.mark.asyncio
async def test_delete(
    repository: ActivityRepository,
    session: AsyncMock,
    activity: Activity,
) -> None:
    """
    delete must mark the activity for deletion and flush
    the pending transaction.
    """

    result = await repository.delete(
        activity=activity,
    )

    assert result is None

    session.delete.assert_awaited_once_with(
        activity,
    )

    session.flush.assert_awaited_once()