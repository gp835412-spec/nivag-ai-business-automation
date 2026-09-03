"""
==========================================================
NIVAG AI Business Automation

Authentication Dependency Compatibility Layer

This module preserves the existing API dependency import
path while delegating authentication to the centralized
security implementation.

The actual authentication and JWT validation logic lives in:

    app.security.dependencies

This module intentionally contains no duplicate JWT logic.
==========================================================
"""

from __future__ import annotations

from app.security.dependencies import (
    CurrentUser,
    bearer_scheme,
    get_current_user,
)

__all__ = [
    "CurrentUser",
    "get_current_user",
    "bearer_scheme",
]