"""
==========================================================
NIVAG AI Business Automation

Password Security

Description:
Secure password hashing and verification using Argon2.

Plain-text passwords must never be persisted, logged,
returned by APIs, or otherwise exposed by the application.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

from pwdlib import PasswordHash


_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using the configured secure
    password hashing algorithm.

    Args:
        password: Plain-text password supplied by the user.

    Returns:
        Secure password hash.

    Raises:
        ValueError: If password is empty or not a string.
    """

    if not isinstance(password, str):
        raise ValueError("password must be a string.")

    if not password:
        raise ValueError("password cannot be empty.")

    return _password_hash.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Verify a plain-text password against a stored password hash.

    Args:
        password: Plain-text password supplied by the user.
        password_hash: Previously generated password hash.

    Returns:
        True when the password matches the stored hash,
        otherwise False.
    """

    if not isinstance(password, str):
        return False

    if not isinstance(password_hash, str):
        return False

    if not password or not password_hash:
        return False

    return _password_hash.verify(
        password,
        password_hash,
    )


__all__ = [
    "hash_password",
    "verify_password",
]