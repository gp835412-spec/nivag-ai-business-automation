"""
==========================================================
NIVAG AI Business Automation

Activity API Routes

Tenant-scoped CRM activity endpoints.

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
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session.database import get_db_session
from app.repositories.activity_repository import ActivityRepository
from app.schemas.activity.create import ActivityCreate
from app.schemas.activity.update import ActivityUpdate
from app.security.dependencies import CurrentUser
from app.services.activity_service import (
    ActivityNotFoundError,
    ActivityService,
    ActivityValidationError,
)


router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
)


def get_activity_service(
    session: AsyncSession = Depends(
        get_db_session,
    ),
) -> ActivityService:
    """
    Return an ActivityService configured with the
    current database session.
    """

    repository = ActivityRepository(
        session,
    )

    return ActivityService(
        repository,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_activity(
    data: ActivityCreate,
    current_user: CurrentUser,
    service: ActivityService = Depends(
        get_activity_service,
    ),
):
    """
    Create a new activity inside the authenticated
    user's organization.
    """

    try:
        return await service.create_activity(
            organization_id=current_user.organization_id,
            data=data,
        )
    except ActivityValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get(
    "",
)
async def list_activities(
    current_user: CurrentUser,
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    service: ActivityService = Depends(
        get_activity_service,
    ),
):
    """
    List activities belonging to the authenticated
    user's organization.
    """

    return await service.list_activities(
        organization_id=current_user.organization_id,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{activity_id}",
)
async def get_activity(
    activity_id: UUID,
    current_user: CurrentUser,
    service: ActivityService = Depends(
        get_activity_service,
    ),
):
    """
    Return one activity belonging to the authenticated
    user's organization.
    """

    try:
        return await service.get_activity(
            organization_id=current_user.organization_id,
            activity_id=activity_id,
        )
    except ActivityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{activity_id}",
)
async def update_activity(
    activity_id: UUID,
    data: ActivityUpdate,
    current_user: CurrentUser,
    service: ActivityService = Depends(
        get_activity_service,
    ),
):
    """
    Update an activity belonging to the authenticated
    user's organization.
    """

    try:
        return await service.update_activity(
            organization_id=current_user.organization_id,
            activity_id=activity_id,
            data=data,
        )
    except ActivityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ActivityValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_activity(
    activity_id: UUID,
    current_user: CurrentUser,
    service: ActivityService = Depends(
        get_activity_service,
    ),
) -> None:
    """
    Delete an activity belonging to the authenticated
    user's organization.
    """

    try:
        await service.delete_activity(
            organization_id=current_user.organization_id,
            activity_id=activity_id,
        )
    except ActivityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


__all__ = [
    "router",
]