"""
==========================================================
NIVAG AI Business Automation

Authentication Dependencies

Responsibilities:
- Extract Bearer token from requests
- Decode and validate JWT access tokens
- Resolve the authenticated user
- Reject invalid or inactive users
- Provide reusable authentication dependencies

Business logic remains inside the service layer.
API routes consume dependencies and must not perform
authentication or token-validation logic directly.
==========================================================
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session.database import get_db_session
from app.models.user import User, UserStatus
from app.security.token import decode_access_token
from app.services.user_service import UserService


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


def _authentication_exception() -> HTTPException:
    """
    Create the standard authentication failure response.

    The response intentionally avoids disclosing whether
    the token was malformed, expired, invalid, or associated
    with a missing user.
    """

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not authenticate credentials.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )


async def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> User:
    """
    Resolve and return the authenticated active user.

    Authentication flow:

        Bearer Token
            ↓
        JWT Decode
            ↓
        Subject Validation
            ↓
        User Lookup
            ↓
        User Status Validation
            ↓
        Authenticated User
    """

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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active.",
        )

    return user


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


__all__ = [
    "CurrentUser",
    "get_current_user",
    "oauth2_scheme",
]