"""
==========================================================
NIVAG AI Business Automation

User Model

Description:
Persistent application user identity and organization
membership model.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base.base import Base
from app.db.base.model_mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class UserStatus(str, enum.Enum):
    """Lifecycle status of an application user."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class UserRole(str, enum.Enum):
    """Application-level authorization role."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class User(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """
    Application user belonging to an organization.

    A user is uniquely identified by email within an
    organization and stores only the password hash.
    Plain-text passwords must never be persisted.
    """

    __tablename__ = "users"

    __table_args__ = (
        Index(
            "ix_users_organization_id",
            "organization_id",
        ),
        Index(
            "ix_users_organization_email",
            "organization_id",
            "email",
            unique=True,
        ),
        Index(
            "ix_users_status",
            "status",
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            native_enum=False,
            length=20,
        ),
        nullable=False,
        default=UserRole.MEMBER,
        server_default=UserRole.MEMBER.value,
    )

    status: Mapped[UserStatus] = mapped_column(
        Enum(
            UserStatus,
            name="user_status",
            native_enum=False,
            length=20,
        ),
        nullable=False,
        default=UserStatus.ACTIVE,
        server_default=UserStatus.ACTIVE.value,
    )

    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    organization: Mapped[Organization] = relationship(
        "Organization",
        back_populates="users",
        lazy="raise",
    )

    def __repr__(self) -> str:
        """Return a safe developer-facing representation."""

        return (
            f"<User("
            f"id={self.id!s}, "
            f"organization_id={self.organization_id!s}, "
            f"email={self.email!r}, "
            f"status={self.status.value!r}"
            f")>"
        )
    
    __all__ = [
       "User",
       "UserRole",
       "UserStatus",
    ]
