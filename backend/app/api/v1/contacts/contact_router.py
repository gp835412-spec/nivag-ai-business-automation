"""
==========================================================
NIVAG AI Business Automation

Contact Router

API endpoints for tenant-scoped CRM contact operations.

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
from app.schemas.contact.contact_schema import (
    ContactCreate,
    ContactListResponse,
    ContactResponse,
    ContactUpdate,
)
from app.services.contact_service import (
    ContactCompanyNotFoundError,
    ContactNotFoundError,
    ContactService,
)

router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"],
)


def get_contact_service(
    session: AsyncSession = Depends(get_db_session),
) -> ContactService:
    """
    Provide the contact service for the current request.
    """

    contact_repository = ContactRepository(session)
    company_repository = CompanyRepository(session)

    return ContactService(
        contact_repository=contact_repository,
        company_repository=company_repository,
    )


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    payload: ContactCreate,
    current_user: User = Depends(get_current_user),
    service: ContactService = Depends(get_contact_service),
) -> ContactResponse:
    """
    Create a contact inside the authenticated user's organization.
    """

    try:
        return await service.create_contact(
            organization_id=current_user.organization_id,
            payload=payload,
        )

    except ContactCompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        ) from exc


@router.get(
    "",
    response_model=ContactListResponse,
)
async def list_contacts(
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
    service: ContactService = Depends(get_contact_service),
) -> ContactListResponse:
    """
    List contacts belonging to the authenticated user's organization.
    """

    return await service.list_contacts(
        organization_id=current_user.organization_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
)
async def get_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ContactService = Depends(get_contact_service),
) -> ContactResponse:
    """
    Get a contact belonging to the authenticated user's organization.
    """

    try:
        return await service.get_contact(
            contact_id=contact_id,
            organization_id=current_user.organization_id,
        )

    except ContactNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found.",
        ) from exc


@router.patch(
    "/{contact_id}",
    response_model=ContactResponse,
)
async def update_contact(
    contact_id: UUID,
    payload: ContactUpdate,
    current_user: User = Depends(get_current_user),
    service: ContactService = Depends(get_contact_service),
) -> ContactResponse:
    """
    Update a contact belonging to the authenticated user's organization.
    """

    try:
        return await service.update_contact(
            contact_id=contact_id,
            organization_id=current_user.organization_id,
            payload=payload,
        )

    except ContactNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found.",
        ) from exc

    except ContactCompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        ) from exc


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ContactService = Depends(get_contact_service),
) -> Response:
    """
    Delete a contact belonging to the authenticated user's organization.
    """

    try:
        await service.delete_contact(
            contact_id=contact_id,
            organization_id=current_user.organization_id,
        )

    except ContactNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found.",
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


__all__ = [
    "get_contact_service",
    "router",
]