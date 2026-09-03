"""
==========================================================
NIVAG AI Business Automation

Authentication Dependencies

Responsibilities:
- Extract Bearer token from requests
- Decode and validate JWT access tokens
- Resolve the authenticated user
- Reject invalid, missing, or inactive users
- Provide reusable authentication dependencies

Authentication validation is centralized here so API routes
do not perform JWT parsing or current-user resolution.
==========================================================
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session.database import get_db_session
from app.models.user import User, UserStatus
from app.security.token import decode_access_token
from app.services.user_service import UserService


bearer_scheme = HTTPBearer(
    auto_error=True,
)


def _authentication_exception() -> HTTPException:
    """
    Create the standard authentication failure response.
    """

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not authenticate credentials.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> User:
    """
    Resolve and return the authenticated active user.
    """

    if credentials.scheme.lower() != "bearer":
        raise _authentication_exception()

    token = credentials.credentials

    try:
        payload = decode_access_token(token)

        subject = payload.get("sub")

        if not isinstance(subject, str):
            raise ValueError(
                "JWT subject is missing.",
            )

        user_id = UUID(subject)

    except (
        ValueError,
        TypeError,
    ) as exc:
        raise _authentication_exception() from exc

    user_service = UserService(session)

    user = await user_service.get_by_id(
        user_id,
    )

    if user is None:
        raise _authentication_exception()

    if user.status != UserStatus.ACTIVE:
        raise _authentication_exception()

    return user


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


__all__ = [
    "CurrentUser",
    "get_current_user",
    "bearer_scheme",
]