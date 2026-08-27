"""
==========================================================
NIVAG AI Business Automation

Activity Service Tests

Unit tests for tenant-scoped CRM activity business logic.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models.activity import (
    Activity,
    ActivityStatus,
    ActivityType,
)
from app.models.company import Company
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.opportunity import Opportunity
from app.schemas.activity.create import ActivityCreate
from app.schemas.activity.update import ActivityUpdate
from app.services.activity_service import (
    ActivityNotFoundError,
    ActivityService,
    ActivityValidationError,
)


@pytest.fixture
def organization_id():
    """Return a test organization ID."""

    return uuid4()


@pytest.fixture
def repository():
    """
    Return a mocked ActivityRepository.

    The repository session is also mocked because the service
    validates related CRM entity references directly through
    repository.session.
    """

    repository_mock = MagicMock()

    repository_mock.create = AsyncMock()
    repository_mock.get_by_id = AsyncMock()
    repository_mock.list = AsyncMock()
    repository_mock.update = AsyncMock()
    repository_mock.delete = AsyncMock()

    repository_mock.session = MagicMock()
    repository_mock.session.get = AsyncMock()

    return repository_mock


@pytest.fixture
def service(repository):
    """Return the ActivityService under test."""

    return ActivityService(
        repository,
    )


@pytest.fixture
def activity_data():
    """Return valid activity creation data."""

    return ActivityCreate(
        activity_type=ActivityType.CALL,
        status=ActivityStatus.PENDING,
        subject="Follow up with customer",
        description="Discuss the proposal.",
        due_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def activity(organization_id):
    """Return a mocked persisted Activity."""

    activity_mock = MagicMock(
        spec=Activity,
    )

    activity_mock.id = uuid4()
    activity_mock.organization_id = organization_id
    activity_mock.company_id = None
    activity_mock.contact_id = None
    activity_mock.lead_id = None
    activity_mock.opportunity_id = None
    activity_mock.activity_type = ActivityType.CALL
    activity_mock.status = ActivityStatus.PENDING
    activity_mock.subject = "Follow up with customer"
    activity_mock.description = "Discuss the proposal."
    activity_mock.due_at = datetime.now(timezone.utc)
    activity_mock.completed_at = None

    return activity_mock


@pytest.mark.asyncio
async def test_create_activity(
    service,
    repository,
    organization_id,
    activity_data,
):
    """
    Service should validate references and create an activity.
    """

    created_activity = MagicMock(
        spec=Activity,
    )

    repository.create.return_value = created_activity

    result = await service.create_activity(
        organization_id=organization_id,
        data=activity_data,
    )

    assert result is created_activity

    repository.create.assert_awaited_once()

    created_argument = repository.create.call_args.kwargs[
        "activity"
    ]

    assert created_argument.organization_id == organization_id
    assert (
        created_argument.activity_type
        == activity_data.activity_type
    )
    assert (
        created_argument.status
        == activity_data.status
    )
    assert (
        created_argument.subject
        == activity_data.subject
    )


@pytest.mark.asyncio
async def test_get_activity_returns_activity(
    service,
    repository,
    organization_id,
    activity,
):
    """
    Service should return an existing tenant-scoped activity.
    """

    repository.get_by_id.return_value = activity

    result = await service.get_activity(
        organization_id=organization_id,
        activity_id=activity.id,
    )

    assert result is activity

    repository.get_by_id.assert_awaited_once_with(
        organization_id=organization_id,
        activity_id=activity.id,
    )


@pytest.mark.asyncio
async def test_get_activity_raises_when_not_found(
    service,
    repository,
    organization_id,
):
    """
    Service should raise ActivityNotFoundError when the
    activity does not exist in the organization.
    """

    activity_id = uuid4()

    repository.get_by_id.return_value = None

    with pytest.raises(
        ActivityNotFoundError,
        match="Activity not found.",
    ):
        await service.get_activity(
            organization_id=organization_id,
            activity_id=activity_id,
        )


@pytest.mark.asyncio
async def test_list_activities(
    service,
    repository,
    organization_id,
):
    """
    Service should delegate tenant-scoped activity listing
    to the repository.
    """

    activities = [
        MagicMock(spec=Activity),
        MagicMock(spec=Activity),
    ]

    repository.list.return_value = activities

    result = await service.list_activities(
        organization_id=organization_id,
        offset=10,
        limit=50,
    )

    assert result == activities

    repository.list.assert_awaited_once_with(
        organization_id=organization_id,
        offset=10,
        limit=50,
    )


@pytest.mark.asyncio
async def test_update_activity(
    service,
    repository,
    organization_id,
    activity,
):
    """
    Service should update only explicitly supplied fields.
    """

    repository.get_by_id.return_value = activity
    repository.update.return_value = activity

    data = ActivityUpdate(
        subject="Updated follow up",
        description="Updated description.",
    )

    result = await service.update_activity(
        organization_id=organization_id,
        activity_id=activity.id,
        data=data,
    )

    assert result is activity
    assert activity.subject == "Updated follow up"
    assert activity.description == "Updated description."

    repository.update.assert_awaited_once_with(
        activity=activity,
    )


@pytest.mark.asyncio
async def test_update_activity_raises_when_not_found(
    service,
    repository,
    organization_id,
):
    """
    Updating a missing activity should raise
    ActivityNotFoundError.
    """

    activity_id = uuid4()

    repository.get_by_id.return_value = None

    data = ActivityUpdate(
        subject="Updated subject",
    )

    with pytest.raises(
        ActivityNotFoundError,
        match="Activity not found.",
    ):
        await service.update_activity(
            organization_id=organization_id,
            activity_id=activity_id,
            data=data,
        )


@pytest.mark.asyncio
async def test_delete_activity(
    service,
    repository,
    organization_id,
    activity,
):
    """
    Service should resolve the activity within the tenant
    and delegate deletion to the repository.
    """

    repository.get_by_id.return_value = activity

    await service.delete_activity(
        organization_id=organization_id,
        activity_id=activity.id,
    )

    repository.delete.assert_awaited_once_with(
        activity=activity,
    )


@pytest.mark.asyncio
async def test_delete_activity_raises_when_not_found(
    service,
    repository,
    organization_id,
):
    """
    Deleting a missing activity should raise
    ActivityNotFoundError.
    """

    activity_id = uuid4()

    repository.get_by_id.return_value = None

    with pytest.raises(
        ActivityNotFoundError,
        match="Activity not found.",
    ):
        await service.delete_activity(
            organization_id=organization_id,
            activity_id=activity_id,
        )


@pytest.mark.asyncio
async def test_create_activity_rejects_invalid_company(
    service,
    repository,
    organization_id,
):
    """
    A referenced company belonging to another organization
    must be rejected.
    """

    company_id = uuid4()

    other_company = MagicMock(
        spec=Company,
    )

    other_company.organization_id = uuid4()

    repository.session.get.return_value = other_company

    data = ActivityCreate(
        company_id=company_id,
        activity_type=ActivityType.CALL,
        status=ActivityStatus.PENDING,
        subject="Follow up",
    )

    with pytest.raises(
        ActivityValidationError,
        match="Invalid company for this organization.",
    ):
        await service.create_activity(
            organization_id=organization_id,
            data=data,
        )

    repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_activity_accepts_valid_company(
    service,
    repository,
    organization_id,
):
    """
    A referenced company belonging to the same organization
    should be accepted.
    """

    company_id = uuid4()

    company = MagicMock(
        spec=Company,
    )

    company.organization_id = organization_id

    repository.session.get.return_value = company

    created_activity = MagicMock(
        spec=Activity,
    )

    repository.create.return_value = created_activity

    data = ActivityCreate(
        company_id=company_id,
        activity_type=ActivityType.CALL,
        status=ActivityStatus.PENDING,
        subject="Follow up",
    )

    result = await service.create_activity(
        organization_id=organization_id,
        data=data,
    )

    assert result is created_activity

    repository.session.get.assert_awaited_once_with(
        Company,
        company_id,
    )


@pytest.mark.asyncio
async def test_create_activity_rejects_invalid_contact(
    service,
    repository,
    organization_id,
):
    """
    A referenced contact belonging to another organization
    must be rejected.
    """

    contact_id = uuid4()

    contact = MagicMock(
        spec=Contact,
    )

    contact.organization_id = uuid4()

    repository.session.get.return_value = contact

    data = ActivityCreate(
        contact_id=contact_id,
        activity_type=ActivityType.EMAIL,
        status=ActivityStatus.PENDING,
        subject="Send proposal",
    )

    with pytest.raises(
        ActivityValidationError,
        match="Invalid contact for this organization.",
    ):
        await service.create_activity(
            organization_id=organization_id,
            data=data,
        )


@pytest.mark.asyncio
async def test_create_activity_rejects_invalid_lead(
    service,
    repository,
    organization_id,
):
    """
    A referenced lead belonging to another organization
    must be rejected.
    """

    lead_id = uuid4()

    lead = MagicMock(
        spec=Lead,
    )

    lead.organization_id = uuid4()

    repository.session.get.return_value = lead

    data = ActivityCreate(
        lead_id=lead_id,
        activity_type=ActivityType.TASK,
        status=ActivityStatus.PENDING,
        subject="Qualify lead",
    )

    with pytest.raises(
        ActivityValidationError,
        match="Invalid lead for this organization.",
    ):
        await service.create_activity(
            organization_id=organization_id,
            data=data,
        )


@pytest.mark.asyncio
async def test_create_activity_rejects_invalid_opportunity(
    service,
    repository,
    organization_id,
):
    """
    A referenced opportunity belonging to another
    organization must be rejected.
    """

    opportunity_id = uuid4()

    opportunity = MagicMock(
        spec=Opportunity,
    )

    opportunity.organization_id = uuid4()

    repository.session.get.return_value = opportunity

    data = ActivityCreate(
        opportunity_id=opportunity_id,
        activity_type=ActivityType.MEETING,
        status=ActivityStatus.PENDING,
        subject="Opportunity meeting",
    )

    with pytest.raises(
        ActivityValidationError,
        match="Invalid opportunity for this organization.",
    ):
        await service.create_activity(
            organization_id=organization_id,
            data=data,
        )


@pytest.mark.asyncio
async def test_completed_activity_requires_completed_at(
    service,
    organization_id,
):
    """
    A completed activity must contain a completion timestamp.
    """

    data = ActivityCreate(
        activity_type=ActivityType.TASK,
        status=ActivityStatus.COMPLETED,
        subject="Complete task",
        completed_at=None,
    )

    with pytest.raises(
        ActivityValidationError,
        match=(
            "completed_at is required when activity status "
            "is completed."
        ),
    ):
        await service.create_activity(
            organization_id=organization_id,
            data=data,
        )


@pytest.mark.asyncio
async def test_incomplete_activity_rejects_completed_at(
    service,
    organization_id,
):
    """
    A non-completed activity must not contain completed_at.
    """

    data = ActivityCreate(
        activity_type=ActivityType.TASK,
        status=ActivityStatus.PENDING,
        subject="Pending task",
        completed_at=datetime.now(
            timezone.utc,
        ),
    )

    with pytest.raises(
        ActivityValidationError,
        match=(
            "completed_at can only be set when activity "
            "status is completed."
        ),
    ):
        await service.create_activity(
            organization_id=organization_id,
            data=data,
        )


@pytest.mark.asyncio
async def test_completed_at_cannot_be_before_due_at(
    service,
    organization_id,
):
    """
    The completion timestamp cannot be earlier than the
    activity due timestamp.
    """

    due_at = datetime.now(
        timezone.utc,
    )

    completed_at = due_at - timedelta(
        hours=1,
    )

    data = ActivityCreate(
        activity_type=ActivityType.MEETING,
        status=ActivityStatus.COMPLETED,
        subject="Customer meeting",
        due_at=due_at,
        completed_at=completed_at,
    )

    with pytest.raises(
        ActivityValidationError,
        match=(
            "completed_at cannot be earlier than due_at."
        ),
    ):
        await service.create_activity(
            organization_id=organization_id,
            data=data,
        )


@pytest.mark.asyncio
async def test_completed_activity_with_valid_dates(
    service,
    repository,
    organization_id,
):
    """
    A completed activity with valid lifecycle timestamps
    should be created successfully.
    """

    due_at = datetime.now(
        timezone.utc,
    )

    completed_at = due_at + timedelta(
        hours=1,
    )

    created_activity = MagicMock(
        spec=Activity,
    )

    repository.create.return_value = created_activity

    data = ActivityCreate(
        activity_type=ActivityType.MEETING,
        status=ActivityStatus.COMPLETED,
        subject="Completed customer meeting",
        due_at=due_at,
        completed_at=completed_at,
    )

    result = await service.create_activity(
        organization_id=organization_id,
        data=data,
    )

    assert result is created_activity

    repository.create.assert_awaited_once()