"""
==========================================================
NIVAG AI Business Automation

Authentication API Router

Responsibilities:
- Registration endpoint
- Login endpoint
- Current authenticated user endpoint
- Request validation
- Service delegation
- HTTP response mapping

Business logic remains inside AuthService.
JWT validation and current-user resolution remain inside
reusable authentication dependencies.
==========================================================
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session.database import get_db_session
from app.models.user import User
from app.schemas.auth import (
    AuthenticatedUserResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
)
from app.security.dependencies import CurrentUser
from app.services.auth import (
    AuthenticationError,
    AuthService,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=AuthenticatedUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> AuthenticatedUserResponse:
    """
    Register a new organization and its owner user.
    """

    service = AuthService(session)

    try:
        user = await service.register(
            organization_name=request.organization_name,
            organization_slug=request.organization_slug,
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            legal_name=request.legal_name,
            last_name=request.last_name,
            phone=request.phone,
            timezone=request.timezone,
            currency=request.currency,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return AuthenticatedUserResponse.model_validate(
        user,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    """
    Authenticate a user and return a JWT access token.
    """

    service = AuthService(session)

    try:
        user, token = await service.login_with_user(
            organization_slug=request.organization_slug,
            email=request.email,
            password=request.password,
        )
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=AuthenticatedUserResponse.model_validate(
            user,
        ),
    )


@router.get(
    "/me",
    response_model=AuthenticatedUserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_current_user(
    current_user: CurrentUser,
) -> AuthenticatedUserResponse:
    """
    Return the currently authenticated user.
    """

    return AuthenticatedUserResponse.model_validate(
        current_user,
    )


__all__ = [
    "router",
]