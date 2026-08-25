"""
==========================================================
NIVAG AI Business Automation

Company Router

API endpoints for tenant-scoped CRM company operations.

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
from app.schemas.company.company_schema import (
    CompanyCreate,
    CompanyListResponse,
    CompanyResponse,
    CompanyUpdate,
)
from app.services.company_service import (
    CompanyNotFoundError,
    CompanyService,
)

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


def get_company_service(
    session: AsyncSession = Depends(get_db_session),
) -> CompanyService:
    """
    Provide the company service for the current request.
    """

    repository = CompanyRepository(session)

    return CompanyService(repository)


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_company(
    payload: CompanyCreate,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    """
    Create a company inside the authenticated user's organization.
    """

    return await service.create_company(
        organization_id=current_user.organization_id,
        payload=payload,
    )


@router.get(
    "",
    response_model=CompanyListResponse,
)
async def list_companies(
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyListResponse:
    """
    List companies belonging to the authenticated user's organization.
    """

    return await service.list_companies(
        organization_id=current_user.organization_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
async def get_company(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    """
    Get a company belonging to the authenticated user's organization.
    """

    try:
        return await service.get_company(
            company_id=company_id,
            organization_id=current_user.organization_id,
        )
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        ) from exc


@router.patch(
    "/{company_id}",
    response_model=CompanyResponse,
)
async def update_company(
    company_id: UUID,
    payload: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    """
    Update a company belonging to the authenticated user's organization.
    """

    try:
        return await service.update_company(
            company_id=company_id,
            organization_id=current_user.organization_id,
            payload=payload,
        )
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        ) from exc


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_company(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> Response:
    """
    Delete a company belonging to the authenticated user's organization.
    """

    try:
        await service.delete_company(
            company_id=company_id,
            organization_id=current_user.organization_id,
        )
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


__all__ = [
    "router",
]