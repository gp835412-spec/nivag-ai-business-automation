"""
Public inquiry API for the NIVAG portfolio.

This endpoint is intentionally separate from the authenticated CRM
lead endpoints. It is the public entry point used by the portfolio
website to submit a business inquiry.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session.database import get_db_session
from app.models.organization import Organization
from app.schemas.lead.lead_schema import LeadCreate
from app.services.lead_service import LeadService
from app.repositories.company_repository import CompanyRepository
from app.repositories.contact_repository import ContactRepository
from app.repositories.lead_repository import LeadRepository
from app.automation.dispatcher import AutomationDispatcher
from app.automation.events import AutomationEventType
from app.automation.lead_handlers import LeadCreatedActivityHandler
from app.repositories.activity_repository import ActivityRepository
from app.services.activity_service import ActivityService

from app.models.organization import Organization, OrganizationStatus

router = APIRouter(
    prefix="/public",
    tags=["Public"],
)


class PublicInquiryRequest(BaseModel):
    """
    Public portfolio inquiry payload.

    Organization routing is intentionally not accepted from the client.
    The public endpoint resolves the target organization server-side.
    """

    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=50)
    company_name: str | None = Field(default=None, max_length=200)
    job_title: str | None = Field(default=None, max_length=200)

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str | None = None
    source: str | None = Field(default="NIVAG Portfolio", max_length=100)


class PublicInquiryResponse(BaseModel):
    """
    Minimal public response.

    CRM internals are deliberately not exposed.
    """

    message: str
    lead_id: UUID


async def _resolve_public_organization(
    session: AsyncSession,
) -> Organization:
    """
    Resolve the organization that owns public portfolio inquiries.

    The public organization is identified by its canonical slug.
    """

    organization = await session.scalar(
        select(Organization)
        .where(
            Organization.slug == "nivag",
            Organization.status == OrganizationStatus.ACTIVE,
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Public inquiry service is not configured.",
        )

    return organization


def _build_lead_service(
    session: AsyncSession,
) -> LeadService:
    """
    Build the LeadService with the same request-scoped session so
    LEAD_CREATED automation participates in the same transaction.
    """

    activity_service = ActivityService(
        repository=ActivityRepository(session),
    )

    automation_dispatcher = AutomationDispatcher()

    automation_dispatcher.register(
        event_type=AutomationEventType.LEAD_CREATED,
        handler=LeadCreatedActivityHandler(
            activity_service=activity_service,
        ),
    )

    return LeadService(
        lead_repository=LeadRepository(session),
        company_repository=CompanyRepository(session),
        contact_repository=ContactRepository(session),
        automation_dispatcher=automation_dispatcher,
    )


@router.post(
    "/inquiries",
    response_model=PublicInquiryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_public_inquiry(
    request: PublicInquiryRequest,
    session: AsyncSession = Depends(get_db_session),
) -> PublicInquiryResponse:
    """
    Accept a public portfolio inquiry and create a CRM lead.

    The authenticated CRM /leads endpoint remains protected.
    This endpoint is the controlled public boundary.
    """

    organization = await _resolve_public_organization(session)

    lead_service = _build_lead_service(session)

    lead_payload = LeadCreate(
        company_id=None,
        contact_id=None,
        title=request.title.strip(),
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        phone=request.phone,
        job_title=request.job_title,
        company_name=request.company_name,
        source=request.source,
        description=request.description,
    )

    try:
        lead = await lead_service.create_lead(
            organization_id=organization.id,
            payload=lead_payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return PublicInquiryResponse(
        message="Inquiry received successfully.",
        lead_id=lead.id,
    )


__all__ = [
    "router",
]
