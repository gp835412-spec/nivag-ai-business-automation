"""
==========================================================
NIVAG AI Business Automation

Organization API Router

Responsibilities:
- Authenticated organization access
- Organization profile retrieval
- Organization profile updates
- Service delegation
- Request validation
- HTTP response mapping

Security:
- Organization identity is always derived from CurrentUser.
- A user cannot access or modify another organization.
- Public organization creation is handled only by registration.
- Business and persistence logic remain outside the router.
==========================================================
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session.database import get_db_session
from app.schemas.organization import (
    OrganizationResponse,
    OrganizationUpdate,
)
from app.security.dependencies import CurrentUser
from app.services.organization_service import OrganizationService


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


def _organization_not_found_exception() -> HTTPException:
    """
    Return the standard organization-not-found response.
    """

    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Organization not found.",
    )


@router.get(
    "/me",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_current_organization(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
) -> OrganizationResponse:
    """
    Return the organization of the authenticated user.
    """

    service = OrganizationService(session)

    organization = await service.get_by_id(
        current_user.organization_id,
    )

    if organization is None:
        raise _organization_not_found_exception()

    return OrganizationResponse.model_validate(
        organization,
    )


@router.patch(
    "/me",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
async def update_current_organization(
    request: OrganizationUpdate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
) -> OrganizationResponse:
    """
    Update the organization of the authenticated user.

    The organization is resolved exclusively from the
    authenticated user's organization_id.
    """

    service = OrganizationService(session)

    organization = await service.get_by_id(
        current_user.organization_id,
    )

    if organization is None:
        raise _organization_not_found_exception()

    update_data = request.model_dump(
        exclude_unset=True,
    )

    for field_name, value in update_data.items():
        setattr(
            organization,
            field_name,
            value,
        )

    try:
        updated = await service.update(
            organization,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return OrganizationResponse.model_validate(
        updated,
    )


__all__ = [
    "router",
]