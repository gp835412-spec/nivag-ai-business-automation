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
    status,
)

from app.schemas.opportunity.create import OpportunityCreate
from app.schemas.opportunity.update import OpportunityUpdate
from app.services.opportunity_service import (
    OpportunityNotFoundError,
    OpportunityService,
    OpportunityValidationError,
)


router = APIRouter(
    prefix="/opportunities",
    tags=["Opportunities"],
)


def get_opportunity_service() -> OpportunityService:
    """
    Return the configured OpportunityService.

    The concrete dependency wiring should provide the
    repository-backed service instance.
    """

    raise NotImplementedError(
        "Opportunity service dependency has not been configured."
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
    """Create a new opportunity."""

    try:
        return await service.create_opportunity(
            organization_id=organization_id,
            data=data,
        )
    except OpportunityValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
    """List opportunities for an organization."""

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
    """Get one opportunity."""

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
    """Update an opportunity."""

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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
) -> None:
    """Delete an opportunity."""

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


__all__ = [
    "router",
]