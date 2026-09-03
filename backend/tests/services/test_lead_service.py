"""
==========================================================
NIVAG AI Business Automation

Lead Service Tests

Tests for tenant-scoped CRM lead business logic.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.automation import AutomationEventType
from app.models.company import Company
from app.models.contact import Contact
from app.models.lead import Lead
from app.repositories.company_repository import CompanyRepository
from app.repositories.contact_repository import ContactRepository
from app.repositories.lead_repository import LeadRepository
from app.schemas.lead.lead_schema import (
    LeadCreate,
    LeadStatus,
    LeadUpdate,
)
from app.services.lead_service import (
    LeadCompanyNotFoundError,
    LeadContactNotFoundError,
    LeadNotFoundError,
    LeadService,
)


@pytest.fixture
def lead_repository() -> AsyncMock:
    """Return a mocked lead repository."""

    return AsyncMock(
        spec=LeadRepository,
    )


@pytest.fixture
def company_repository() -> AsyncMock:
    """Return a mocked company repository."""

    return AsyncMock(
        spec=CompanyRepository,
    )


@pytest.fixture
def contact_repository() -> AsyncMock:
    """Return a mocked contact repository."""

    return AsyncMock(
        spec=ContactRepository,
    )


@pytest.fixture
def automation_dispatcher() -> AsyncMock:
    """Return a mocked automation dispatcher."""

    return AsyncMock()


@pytest.fixture
def service(
    lead_repository: AsyncMock,
    company_repository: AsyncMock,
    contact_repository: AsyncMock,
    automation_dispatcher: AsyncMock,
) -> LeadService:
    """Return a configured lead service."""

    return LeadService(
        lead_repository=lead_repository,
        company_repository=company_repository,
        contact_repository=contact_repository,
        automation_dispatcher=automation_dispatcher,
    )


def build_lead(
    *,
    organization_id=None,
    lead_id=None,
    company_id=None,
    contact_id=None,
    title: str = "New Business Opportunity",
    first_name: str | None = "John",
    last_name: str | None = "Doe",
    email: str | None = "john@example.com",
    phone: str | None = None,
    job_title: str | None = None,
    company_name: str | None = None,
    source: str | None = None,
    status: str = LeadStatus.NEW.value,
    estimated_value: Decimal | None = None,
    currency: str = "INR",
    description: str | None = None,
) -> Lead:
    """Build a Lead instance compatible with the current model."""

    now = datetime.now(
        timezone.utc,
    )

    return Lead(
        id=lead_id or uuid4(),
        organization_id=organization_id or uuid4(),
        company_id=company_id,
        contact_id=contact_id,
        title=title,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        job_title=job_title,
        company_name=company_name,
        source=source,
        status=status,
        estimated_value=estimated_value,
        currency=currency,
        description=description,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_create_lead(
    service: LeadService,
    lead_repository: AsyncMock,
) -> None:
    """A lead can be created without company or contact."""

    organization_id = uuid4()

    payload = LeadCreate(
        title="Website Inquiry",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        status=LeadStatus.NEW,
        source="website",
        estimated_value=Decimal("25000.00"),
        currency="INR",
    )

    created_lead = build_lead(
        organization_id=organization_id,
        title=payload.title,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=str(payload.email),
        status=payload.status.value,
        source=payload.source,
        estimated_value=payload.estimated_value,
        currency=payload.currency,
    )

    lead_repository.create.return_value = created_lead

    result = await service.create_lead(
        organization_id=organization_id,
        payload=payload,
    )

    assert result.id == created_lead.id
    assert result.organization_id == organization_id
    assert result.title == "Website Inquiry"
    assert result.first_name == "John"
    assert result.email == "john@example.com"

    lead_repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_lead_dispatches_created_event(
    service: LeadService,
    lead_repository: AsyncMock,
    automation_dispatcher: AsyncMock,
) -> None:
    """Creating a lead dispatches a lead.created event."""

    organization_id = uuid4()

    payload = LeadCreate(
        title="Automation Test Lead",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        status=LeadStatus.NEW,
    )

    created_lead = build_lead(
        organization_id=organization_id,
        title=payload.title,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=str(payload.email),
        status=payload.status.value,
    )

    lead_repository.create.return_value = created_lead

    result = await service.create_lead(
        organization_id=organization_id,
        payload=payload,
    )

    assert result.id == created_lead.id

    automation_dispatcher.dispatch.assert_awaited_once()

    event = automation_dispatcher.dispatch.await_args.args[0]

    assert event.event_type == AutomationEventType.LEAD_CREATED
    assert event.organization_id == organization_id
    assert event.entity_id == created_lead.id
    assert event.payload["lead_id"] == str(
        created_lead.id,
    )
    assert event.payload["organization_id"] == str(
        organization_id,
    )
    assert event.payload["title"] == created_lead.title
    assert event.payload["status"] == created_lead.status


@pytest.mark.asyncio
async def test_update_lead_dispatches_updated_event(
    service: LeadService,
    lead_repository: AsyncMock,
    automation_dispatcher: AsyncMock,
) -> None:
    """Updating a lead dispatches a lead.updated event."""

    organization_id = uuid4()
    lead_id = uuid4()

    lead = build_lead(
        lead_id=lead_id,
        organization_id=organization_id,
        title="Original Lead",
        status=LeadStatus.NEW.value,
    )

    lead_repository.get_by_id.return_value = lead
    lead_repository.update.return_value = lead

    payload = LeadUpdate(
        title="Updated Lead",
    )

    result = await service.update_lead(
        organization_id=organization_id,
        lead_id=lead_id,
        payload=payload,
    )

    assert result.id == lead_id

    automation_dispatcher.dispatch.assert_awaited_once()

    event = automation_dispatcher.dispatch.await_args.args[0]

    assert event.event_type == AutomationEventType.LEAD_UPDATED
    assert event.organization_id == organization_id
    assert event.entity_id == lead_id
    assert event.payload["lead_id"] == str(lead_id)
    assert event.payload["organization_id"] == str(organization_id)
    assert event.payload["title"] == lead.title
    assert event.payload["status"] == lead.status


@pytest.mark.asyncio
async def test_update_lead_dispatches_status_changed_event(
    service: LeadService,
    lead_repository: AsyncMock,
    automation_dispatcher: AsyncMock,
) -> None:
    """Changing a lead status dispatches a lead.status_changed event."""

    organization_id = uuid4()
    lead_id = uuid4()

    lead = build_lead(
        lead_id=lead_id,
        organization_id=organization_id,
        title="Status Change Lead",
        status=LeadStatus.NEW.value,
    )

    lead_repository.get_by_id.return_value = lead
    lead_repository.update.return_value = lead

    payload = LeadUpdate(
        status=LeadStatus.QUALIFIED,
    )

    result = await service.update_lead(
        organization_id=organization_id,
        lead_id=lead_id,
        payload=payload,
    )

    assert result.id == lead_id

    assert automation_dispatcher.dispatch.await_count == 2

    events = [
        call.args[0]
        for call in automation_dispatcher.dispatch.await_args_list
    ]

    updated_event = events[0]
    status_changed_event = events[1]

    assert updated_event.event_type == AutomationEventType.LEAD_UPDATED

    assert status_changed_event.event_type == (
        AutomationEventType.LEAD_STATUS_CHANGED
    )
    assert status_changed_event.organization_id == organization_id
    assert status_changed_event.entity_id == lead_id
    assert status_changed_event.payload["lead_id"] == str(lead_id)
    assert status_changed_event.payload["organization_id"] == str(
        organization_id
    )
    assert status_changed_event.payload["previous_status"] == LeadStatus.NEW.value
    assert status_changed_event.payload["new_status"] == LeadStatus.QUALIFIED.value


@pytest.mark.asyncio
async def test_update_lead_does_not_dispatch_status_changed_when_status_unchanged(
    service: LeadService,
    lead_repository: AsyncMock,
    automation_dispatcher: AsyncMock,
) -> None:
    """Updating other fields without changing status emits no status event."""

    organization_id = uuid4()
    lead_id = uuid4()

    lead = build_lead(
        lead_id=lead_id,
        organization_id=organization_id,
        title="Unchanged Status Lead",
        status=LeadStatus.NEW.value,
    )

    lead_repository.get_by_id.return_value = lead
    lead_repository.update.return_value = lead

    payload = LeadUpdate(
        title="Updated Without Status Change",
    )

    result = await service.update_lead(
        organization_id=organization_id,
        lead_id=lead_id,
        payload=payload,
    )

    assert result.id == lead_id

    automation_dispatcher.dispatch.assert_awaited_once()

    event = automation_dispatcher.dispatch.await_args.args[0]

    assert event.event_type == AutomationEventType.LEAD_UPDATED

    assert not any(
        call.args[0].event_type == AutomationEventType.LEAD_STATUS_CHANGED
        for call in automation_dispatcher.dispatch.await_args_list
    )


@pytest.mark.asyncio
async def test_update_lead_validation_failure_dispatches_no_event(
    service: LeadService,
    lead_repository: AsyncMock,
    company_repository: AsyncMock,
    automation_dispatcher: AsyncMock,
) -> None:
    """Validation failure prevents automation event dispatch."""

    organization_id = uuid4()
    lead_id = uuid4()
    invalid_company_id = uuid4()

    lead = build_lead(
        lead_id=lead_id,
        organization_id=organization_id,
        title="Validation Failure Lead",
        status=LeadStatus.NEW.value,
    )

    lead_repository.get_by_id.return_value = lead
    company_repository.get_by_id.return_value = None

    payload = LeadUpdate(
        company_id=invalid_company_id,
    )

    with pytest.raises(Exception):
        await service.update_lead(
            organization_id=organization_id,
            lead_id=lead_id,
            payload=payload,
        )

    automation_dispatcher.dispatch.assert_not_awaited()
    lead_repository.update.assert_not_awaited()

@pytest.mark.asyncio
async def test_create_lead_with_company(
    service: LeadService,
    lead_repository: AsyncMock,
    company_repository: AsyncMock,
) -> None:
    """A lead may be created with a company from the same tenant."""

    organization_id = uuid4()
    company_id = uuid4()

    payload = LeadCreate(
        company_id=company_id,
        title="Enterprise Opportunity",
        first_name="John",
    )

    company = Company(
        id=company_id,
        organization_id=organization_id,
        name="Acme",
    )

    created_lead = build_lead(
        organization_id=organization_id,
        company_id=company_id,
        title=payload.title,
        first_name="John",
    )

    company_repository.get_by_id.return_value = company
    lead_repository.create.return_value = created_lead

    result = await service.create_lead(
        organization_id=organization_id,
        payload=payload,
    )

    assert result.company_id == company_id

    company_repository.get_by_id.assert_awaited_once_with(
        company_id=company_id,
        organization_id=organization_id,
    )

    lead_repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_lead_raises_when_company_not_found(
    service: LeadService,
    company_repository: AsyncMock,
) -> None:
    """Creating a lead fails when the company is unavailable."""

    organization_id = uuid4()

    payload = LeadCreate(
        company_id=uuid4(),
        title="Company Validation",
        first_name="John",
    )

    company_repository.get_by_id.return_value = None

    with pytest.raises(
        LeadCompanyNotFoundError,
    ):
        await service.create_lead(
            organization_id=organization_id,
            payload=payload,
        )


@pytest.mark.asyncio
async def test_create_lead_with_contact(
    service: LeadService,
    lead_repository: AsyncMock,
    contact_repository: AsyncMock,
) -> None:
    """A lead may be created with a contact from the same tenant."""

    organization_id = uuid4()
    contact_id = uuid4()

    payload = LeadCreate(
        contact_id=contact_id,
        title="Contact Opportunity",
        first_name="John",
    )

    contact = Contact(
        id=contact_id,
        organization_id=organization_id,
        first_name="Existing Contact",
    )

    created_lead = build_lead(
        organization_id=organization_id,
        contact_id=contact_id,
        title=payload.title,
        first_name="John",
    )

    contact_repository.get_by_id.return_value = contact
    lead_repository.create.return_value = created_lead

    result = await service.create_lead(
        organization_id=organization_id,
        payload=payload,
    )

    assert result.contact_id == contact_id

    contact_repository.get_by_id.assert_awaited_once_with(
        contact_id=contact_id,
        organization_id=organization_id,
    )


@pytest.mark.asyncio
async def test_create_lead_raises_when_contact_not_found(
    service: LeadService,
    contact_repository: AsyncMock,
) -> None:
    """Creating a lead fails when the contact is unavailable."""

    organization_id = uuid4()

    payload = LeadCreate(
        contact_id=uuid4(),
        title="Contact Validation",
        first_name="John",
    )

    contact_repository.get_by_id.return_value = None

    with pytest.raises(
        LeadContactNotFoundError,
    ):
        await service.create_lead(
            organization_id=organization_id,
            payload=payload,
        )


@pytest.mark.asyncio
async def test_get_lead(
    service: LeadService,
    lead_repository: AsyncMock,
) -> None:
    """A lead can be retrieved from its organization."""

    organization_id = uuid4()
    lead_id = uuid4()

    lead = build_lead(
        lead_id=lead_id,
        organization_id=organization_id,
    )

    lead_repository.get_by_id.return_value = lead

    result = await service.get_lead(
        lead_id=lead_id,
        organization_id=organization_id,
    )

    assert result.id == lead_id
    assert result.organization_id == organization_id


@pytest.mark.asyncio
async def test_get_lead_raises_when_not_found(
    service: LeadService,
    lead_repository: AsyncMock,
) -> None:
    """Getting an unknown lead raises LeadNotFoundError."""

    lead_repository.get_by_id.return_value = None

    with pytest.raises(
        LeadNotFoundError,
    ):
        await service.get_lead(
            lead_id=uuid4(),
            organization_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_list_leads(
    service: LeadService,
    lead_repository: AsyncMock,
) -> None:
    """Leads are returned with pagination metadata."""

    organization_id = uuid4()

    leads = [
        build_lead(
            organization_id=organization_id,
            first_name="John",
            title="First Opportunity",
        ),
        build_lead(
            organization_id=organization_id,
            first_name="Jane",
            title="Second Opportunity",
        ),
    ]

    lead_repository.list.return_value = leads
    lead_repository.count.return_value = 2

    result = await service.list_leads(
        organization_id=organization_id,
        limit=50,
        offset=0,
    )

    assert len(result.items) == 2
    assert result.total == 2
    assert result.limit == 50
    assert result.offset == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("limit", "offset"),
    [
        (0, 0),
        (101, 0),
        (50, -1),
    ],
)
async def test_list_leads_rejects_invalid_pagination(
    service: LeadService,
    limit: int,
    offset: int,
) -> None:
    """Invalid pagination values are rejected."""

    with pytest.raises(
        ValueError,
    ):
        await service.list_leads(
            organization_id=uuid4(),
            limit=limit,
            offset=offset,
        )


@pytest.mark.asyncio
async def test_update_lead(
    service: LeadService,
    lead_repository: AsyncMock,
) -> None:
    """A lead can be partially updated."""

    organization_id = uuid4()
    lead_id = uuid4()

    lead = build_lead(
        lead_id=lead_id,
        organization_id=organization_id,
        first_name="John",
        title="Original Opportunity",
        status=LeadStatus.NEW.value,
    )

    payload = LeadUpdate(
        first_name="Updated John",
        status=LeadStatus.QUALIFIED,
    )

    updated_lead = build_lead(
        lead_id=lead_id,
        organization_id=organization_id,
        first_name="Updated John",
        title="Original Opportunity",
        status=LeadStatus.QUALIFIED.value,
    )

    lead_repository.get_by_id.return_value = lead
    lead_repository.update.return_value = updated_lead

    result = await service.update_lead(
        lead_id=lead_id,
        organization_id=organization_id,
        payload=payload,
    )

    assert result.first_name == "Updated John"
    assert result.status == LeadStatus.QUALIFIED


@pytest.mark.asyncio
async def test_update_lead_raises_when_not_found(
    service: LeadService,
    lead_repository: AsyncMock,
) -> None:
    """Updating an unknown lead raises LeadNotFoundError."""

    lead_repository.get_by_id.return_value = None

    with pytest.raises(
        LeadNotFoundError,
    ):
        await service.update_lead(
            lead_id=uuid4(),
            organization_id=uuid4(),
            payload=LeadUpdate(
                first_name="Updated",
            ),
        )


@pytest.mark.asyncio
async def test_update_lead_validates_company(
    service: LeadService,
    lead_repository: AsyncMock,
    company_repository: AsyncMock,
) -> None:
    """Updating company_id validates tenant ownership."""

    organization_id = uuid4()
    lead_id = uuid4()
    company_id = uuid4()

    lead = build_lead(
        lead_id=lead_id,
        organization_id=organization_id,
    )

    company = Company(
        id=company_id,
        organization_id=organization_id,
        name="Acme",
    )

    lead_repository.get_by_id.return_value = lead
    company_repository.get_by_id.return_value = company
    lead_repository.update.return_value = lead

    await service.update_lead(
        lead_id=lead_id,
        organization_id=organization_id,
        payload=LeadUpdate(
            company_id=company_id,
        ),
    )

    company_repository.get_by_id.assert_awaited_once_with(
        company_id=company_id,
        organization_id=organization_id,
    )


@pytest.mark.asyncio
async def test_update_lead_validates_contact(
    service: LeadService,
    lead_repository: AsyncMock,
    contact_repository: AsyncMock,
) -> None:
    """Updating contact_id validates tenant ownership."""

    organization_id = uuid4()
    lead_id = uuid4()
    contact_id = uuid4()

    lead = build_lead(
        lead_id=lead_id,
        organization_id=organization_id,
    )

    contact = Contact(
        id=contact_id,
        organization_id=organization_id,
        first_name="Existing Contact",
    )

    lead_repository.get_by_id.return_value = lead
    contact_repository.get_by_id.return_value = contact
    lead_repository.update.return_value = lead

    await service.update_lead(
        lead_id=lead_id,
        organization_id=organization_id,
        payload=LeadUpdate(
            contact_id=contact_id,
        ),
    )

    contact_repository.get_by_id.assert_awaited_once_with(
        contact_id=contact_id,
        organization_id=organization_id,
    )


@pytest.mark.asyncio
async def test_delete_lead(
    service: LeadService,
    lead_repository: AsyncMock,
) -> None:
    """A lead can be deleted within its organization."""

    organization_id = uuid4()
    lead_id = uuid4()

    lead = build_lead(
        lead_id=lead_id,
        organization_id=organization_id,
    )

    lead_repository.get_by_id.return_value = lead

    await service.delete_lead(
        lead_id=lead_id,
        organization_id=organization_id,
    )

    lead_repository.delete.assert_awaited_once_with(
        lead,
    )


@pytest.mark.asyncio
async def test_delete_lead_raises_when_not_found(
    service: LeadService,
    lead_repository: AsyncMock,
) -> None:
    """Deleting an unknown lead raises LeadNotFoundError."""

    lead_repository.get_by_id.return_value = None

    with pytest.raises(
        LeadNotFoundError,
    ):
        await service.delete_lead(
            lead_id=uuid4(),
            organization_id=uuid4(),
        )