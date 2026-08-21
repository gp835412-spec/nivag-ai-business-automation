"""
==========================================================
NIVAG AI Business Automation

JWT Token Security

Description:
JWT creation and validation for authenticated application
sessions.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt import InvalidTokenError

from app.core.config import settings


class TokenValidationError(ValueError):
    """Raised when a JWT cannot be validated."""


def create_access_token(
    subject: str,
    *,
    expires_minutes: int | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: Stable identifier of the authenticated principal.
        expires_minutes: Token lifetime in minutes. When omitted,
            the configured application value is used.
        additional_claims: Optional additional JWT claims.

    Returns:
        Encoded JWT access token.

    Raises:
        ValueError: If the subject or configured secret is invalid.
    """

    if not isinstance(subject, str) or not subject.strip():
        raise ValueError("subject cannot be empty.")

    if not settings.jwt_secret_key:
        raise ValueError(
            "JWT_SECRET_KEY must be configured before creating tokens."
        )

    lifetime = (
        settings.access_token_expire_minutes
        if expires_minutes is None
        else expires_minutes
    )

    if lifetime < 1:
        raise ValueError(
            "expires_minutes must be greater than or equal to 1."
        )

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=lifetime)

    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": expires_at,
    }

    if additional_claims:
        payload.update(additional_claims)

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Validate and decode a JWT access token.

    Args:
        token: Encoded JWT access token.

    Returns:
        Decoded JWT claims.

    Raises:
        TokenValidationError: If the token is malformed,
            expired, incorrectly signed, or missing a subject.
    """

    if not isinstance(token, str) or not token.strip():
        raise TokenValidationError("Access token is required.")

    if not settings.jwt_secret_key:
        raise TokenValidationError(
            "JWT_SECRET_KEY is not configured."
        )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except InvalidTokenError as exc:
        raise TokenValidationError(
            "Invalid or expired access token."
        ) from exc

    subject = payload.get("sub")

    if not isinstance(subject, str) or not subject.strip():
        raise TokenValidationError(
            "Access token subject is missing."
        )

    return payload


__all__ = [
    "TokenValidationError",
    "create_access_token",
    "decode_access_token",
]