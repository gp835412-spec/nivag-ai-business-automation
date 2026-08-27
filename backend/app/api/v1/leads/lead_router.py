"""
==========================================================
NIVAG AI Business Automation

Lead API Router

HTTP endpoints for tenant-scoped CRM lead operations.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import get_current_user
from app.db.session.database import get_db_session
from app.models.user import User
from app.repositories.company_repository import CompanyRepository
from app.repositories.contact_repository import ContactRepository
from app.repositories.lead_repository import LeadRepository
from app.schemas.lead.lead_schema import (
    LeadCreate,
    LeadListResponse,
    LeadResponse,
    LeadUpdate,
)
from app.services.lead_service import (
    LeadCompanyNotFoundError,
    LeadContactNotFoundError,
    LeadNotFoundError,
    LeadService,
)

router = APIRouter(
    prefix="/leads",
    tags=["Leads"],
)


def get_lead_service(
    session: AsyncSession = Depends(
        get_db_session,
    ),
) -> LeadService:
    """
    Provide the lead service with all required repository
    dependencies.
    """

    return LeadService(
        lead_repository=LeadRepository(
            session,
        ),
        company_repository=CompanyRepository(
            session,
        ),
        contact_repository=ContactRepository(
            session,
        ),
    )


@router.post(
    "",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead(
    payload: LeadCreate,
    current_user: User = Depends(
        get_current_user,
    ),
    service: LeadService = Depends(
        get_lead_service,
    ),
) -> LeadResponse:
    """
    Create a lead inside the authenticated user's organization.
    """

    try:
        return await service.create_lead(
            organization_id=current_user.organization_id,
            payload=payload,
        )
    except (
        LeadCompanyNotFoundError,
        LeadContactNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "",
    response_model=LeadListResponse,
)
async def list_leads(
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    service: LeadService = Depends(
        get_lead_service,
    ),
) -> LeadListResponse:
    """
    List leads belonging to the authenticated user's organization.
    """

    return await service.list_leads(
        organization_id=current_user.organization_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
)
async def get_lead(
    lead_id: UUID,
    current_user: User = Depends(
        get_current_user,
    ),
    service: LeadService = Depends(
        get_lead_service,
    ),
) -> LeadResponse:
    """
    Get a lead belonging to the authenticated user's organization.
    """

    try:
        return await service.get_lead(
            lead_id=lead_id,
            organization_id=current_user.organization_id,
        )
    except LeadNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.patch(
    "/{lead_id}",
    response_model=LeadResponse,
)
async def update_lead(
    lead_id: UUID,
    payload: LeadUpdate,
    current_user: User = Depends(
        get_current_user,
    ),
    service: LeadService = Depends(
        get_lead_service,
    ),
) -> LeadResponse:
    """
    Update a lead belonging to the authenticated user's organization.
    """

    try:
        return await service.update_lead(
            lead_id=lead_id,
            organization_id=current_user.organization_id,
            payload=payload,
        )
    except (
        LeadNotFoundError,
        LeadCompanyNotFoundError,
        LeadContactNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete(
    "/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_lead(
    lead_id: UUID,
    current_user: User = Depends(
        get_current_user,
    ),
    service: LeadService = Depends(
        get_lead_service,
    ),
) -> Response:
    """
    Delete a lead belonging to the authenticated user's organization.
    """

    try:
        await service.delete_lead(
            lead_id=lead_id,
            organization_id=current_user.organization_id,
        )
    except LeadNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


__all__ = [
    "router",
]