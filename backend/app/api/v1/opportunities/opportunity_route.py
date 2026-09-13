"""
==========================================================
NIVAG AI Business Automation

Opportunity API Routes

Tenant-scoped CRM opportunity endpoints.

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

from app.automation import (
    AutomationDispatcher,
    AutomationEventType,
    OpportunityCreatedActivityHandler,
)
from app.db.session.database import get_db_session
from app.repositories.activity_repository import ActivityRepository
from app.repositories.opportunity_repository import OpportunityRepository
from app.schemas.opportunity.create import OpportunityCreate
from app.schemas.opportunity.update import OpportunityUpdate
from app.services.activity_service import ActivityService
from app.services.opportunity_service import (
    OpportunityNotFoundError,
    OpportunityService,
    OpportunityValidationError,
)


router = APIRouter(
    prefix="/opportunities",
    tags=["Opportunities"],
)


def get_opportunity_service(
    session: AsyncSession = Depends(
        get_db_session,
    ),
) -> OpportunityService:
    """Provide the opportunity service for the request."""

    repository = OpportunityRepository(
        session,
    )

    activity_service = ActivityService(
        repository=ActivityRepository(
            session,
        ),
    )

    automation_dispatcher = AutomationDispatcher()

    automation_dispatcher.register(
        AutomationEventType.OPPORTUNITY_CREATED,
        OpportunityCreatedActivityHandler(
            activity_service=activity_service,
        ),
    )

    return OpportunityService(
        repository=repository,
        automation_dispatcher=automation_dispatcher,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_opportunity(
    data: OpportunityCreate,
    organization_id: UUID,
    service: OpportunityService = Depends(
        get_opportunity_service,
    ),
):
    """Create an opportunity for the specified organization."""

    try:
        return await service.create_opportunity(
            organization_id=organization_id,
            data=data,
        )
    except OpportunityValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
)
async def list_opportunities(
    organization_id: UUID,
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    service: OpportunityService = Depends(
        get_opportunity_service,
    ),
):
    """List opportunities for the specified organization."""

    return await service.list_opportunities(
        organization_id=organization_id,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{opportunity_id}",
)
async def get_opportunity(
    opportunity_id: UUID,
    organization_id: UUID,
    service: OpportunityService = Depends(
        get_opportunity_service,
    ),
):
    """Return one opportunity for the specified organization."""

    try:
        return await service.get_opportunity(
            organization_id=organization_id,
            opportunity_id=opportunity_id,
        )
    except OpportunityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{opportunity_id}",
)
async def update_opportunity(
    opportunity_id: UUID,
    data: OpportunityUpdate,
    organization_id: UUID,
    service: OpportunityService = Depends(
        get_opportunity_service,
    ),
):
    """Update an opportunity for the specified organization."""

    try:
        return await service.update_opportunity(
            organization_id=organization_id,
            opportunity_id=opportunity_id,
            data=data,
        )
    except OpportunityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except OpportunityValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{opportunity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_opportunity(
    opportunity_id: UUID,
    organization_id: UUID,
    service: OpportunityService = Depends(
        get_opportunity_service,
    ),
) -> Response:
    """Delete an opportunity for the specified organization."""

    try:
        await service.delete_opportunity(
            organization_id=organization_id,
            opportunity_id=opportunity_id,
        )
    except OpportunityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


__all__ = [
    "router",
]