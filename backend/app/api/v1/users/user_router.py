"""
==========================================================
NIVAG AI Business Automation

User API Router

Responsibilities:
- Organization-scoped user management
- Request validation
- Authenticated user resolution
- Service delegation
- HTTP response mapping

Security:
- organization_id is always derived from CurrentUser
- Users cannot access users from another organization
- Business and persistence logic remain outside the router
==========================================================
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session.database import get_db_session
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)
from app.security.dependencies import CurrentUser
from app.services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def _not_found_exception() -> HTTPException:
    """
    Return the standard user-not-found response.
    """

    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found.",
    )


async def _get_organization_user(
    *,
    user_id: UUID,
    current_user: User,
    service: UserService,
) -> User:
    """
    Resolve a user only when it belongs to the authenticated
    user's organization.

    Cross-organization access is intentionally represented as
    a 404 response so tenant data is not disclosed.
    """

    user = await service.get_by_id(user_id)

    if (
        user is None
        or user.organization_id != current_user.organization_id
    ):
        raise _not_found_exception()

    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    request: UserCreateRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """
    Create a new user inside the authenticated organization.

    Only organization owners and administrators may create users.
    """

    if current_user.role not in {
        UserRole.OWNER,
        UserRole.ADMIN,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create users.",
        )

    service = UserService(session)

    try:
        user = await service.create(
            organization_id=current_user.organization_id,
            email=str(request.email),
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            role=request.role,
        )

        await session.commit()

        await session.refresh(user)

    except ValueError as exc:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except Exception:
        await session.rollback()
        raise

    return UserResponse.model_validate(user)


@router.get(
    "",
    response_model=UserListResponse,
)
async def list_users(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
) -> UserListResponse:
    """
    List users belonging only to the authenticated organization.
    """

    service = UserService(session)

    users = await service.list_by_organization(
        current_user.organization_id,
        offset=offset,
        limit=limit,
    )

    return UserListResponse(
        items=[
            UserResponse.model_validate(user)
            for user in users
        ],
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """
    Return a user from the authenticated organization.
    """

    service = UserService(session)

    user = await _get_organization_user(
        user_id=user_id,
        current_user=current_user,
        service=service,
    )

    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user(
    user_id: UUID,
    request: UserUpdateRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """
    Update a user belonging to the authenticated organization.

    Only organization owners and administrators may update users.
    """

    if current_user.role not in {
        UserRole.OWNER,
        UserRole.ADMIN,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update users.",
        )

    service = UserService(session)

    user = await _get_organization_user(
        user_id=user_id,
        current_user=current_user,
        service=service,
    )

    try:
        updated = await service.update(
            user,
            **request.model_dump(
                exclude_unset=True,
            ),
        )

        await session.commit()

        await session.refresh(updated)

    except ValueError as exc:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except Exception:
        await session.rollback()
        raise

    return UserResponse.model_validate(updated)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Delete a user from the authenticated organization.

    Only organization owners and administrators may delete users.
    """

    if current_user.role not in {
        UserRole.OWNER,
        UserRole.ADMIN,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete users.",
        )

    service = UserService(session)

    user = await _get_organization_user(
        user_id=user_id,
        current_user=current_user,
        service=service,
    )

    try:
        deleted = await service.delete(user)

        if not deleted:
            await session.rollback()
            raise _not_found_exception()

        await session.commit()

    except HTTPException:
        raise

    except Exception:
        await session.rollback()
        raise


__all__ = [
    "router",
]