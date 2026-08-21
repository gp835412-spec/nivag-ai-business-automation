"""
==========================================================
NIVAG AI Business Automation

User API Schemas

Request and response contracts for user management.

Responsibilities:
- User creation requests
- User update requests
- User response serialization
- User list responses
- API-level validation

Business rules remain inside the service layer.
==========================================================
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole, UserStatus


class UserCreateRequest(BaseModel):
    """
    Request payload for creating a user inside the
    authenticated user's organization.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    first_name: str = Field(
        min_length=1,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        max_length=32,
    )

    role: UserRole = UserRole.MEMBER


class UserUpdateRequest(BaseModel):
    """
    Request payload for updating an existing user.

    Only explicitly supplied fields are updated.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    email: EmailStr | None = None

    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        max_length=32,
    )

    role: UserRole | None = None

    status: UserStatus | None = None

    is_email_verified: bool | None = None


class UserResponse(BaseModel):
    """
    Public API representation of an application user.

    Sensitive fields such as password_hash are never exposed.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    organization_id: UUID

    email: EmailStr

    first_name: str

    last_name: str | None

    phone: str | None

    role: UserRole

    status: UserStatus

    is_email_verified: bool


class UserListResponse(BaseModel):
    """
    Response contract for organization user listings.
    """

    items: list[UserResponse]

    offset: int

    limit: int


__all__ = [
    "UserCreateRequest",
    "UserListResponse",
    "UserResponse",
    "UserUpdateRequest",
]