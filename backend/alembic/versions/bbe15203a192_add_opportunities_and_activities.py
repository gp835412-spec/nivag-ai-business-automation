"""
add activities

Revision ID: bbe15203a192
Revises: fa9485ea5dd1
Create Date: 2026-08-28 03:42:51.121393
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bbe15203a192"
down_revision: Union[str, Sequence[str], None] = "fa9485ea5dd1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "activities",
        sa.Column(
            "organization_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "company_id",
            sa.UUID(),
            nullable=True,
        ),
        sa.Column(
            "contact_id",
            sa.UUID(),
            nullable=True,
        ),
        sa.Column(
            "lead_id",
            sa.UUID(),
            nullable=True,
        ),
        sa.Column(
            "opportunity_id",
            sa.UUID(),
            nullable=True,
        ),
        sa.Column(
            "activity_type",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "subject",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "due_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name=op.f(
                "fk_activities_company_id_companies",
            ),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["contact_id"],
            ["contacts.id"],
            name=op.f(
                "fk_activities_contact_id_contacts",
            ),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name=op.f(
                "fk_activities_lead_id_leads",
            ),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["opportunity_id"],
            ["opportunities.id"],
            name=op.f(
                "fk_activities_opportunity_id_opportunities",
            ),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f(
                "fk_activities_organization_id_organizations",
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_activities"),
        ),
    )

    op.create_index(
        op.f("ix_activities_activity_type"),
        "activities",
        ["activity_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_activities_company_id"),
        "activities",
        ["company_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_activities_contact_id"),
        "activities",
        ["contact_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_activities_lead_id"),
        "activities",
        ["lead_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_activities_opportunity_id"),
        "activities",
        ["opportunity_id"],
        unique=False,
    )

    op.create_index(
        "ix_activities_organization_company_id",
        "activities",
        [
            "organization_id",
            "company_id",
        ],
        unique=False,
    )

    op.create_index(
        "ix_activities_organization_contact_id",
        "activities",
        [
            "organization_id",
            "contact_id",
        ],
        unique=False,
    )

    op.create_index(
        "ix_activities_organization_due_at",
        "activities",
        [
            "organization_id",
            "due_at",
        ],
        unique=False,
    )

    op.create_index(
        op.f("ix_activities_organization_id"),
        "activities",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        "ix_activities_organization_lead_id",
        "activities",
        [
            "organization_id",
            "lead_id",
        ],
        unique=False,
    )

    op.create_index(
        "ix_activities_organization_opportunity_id",
        "activities",
        [
            "organization_id",
            "opportunity_id",
        ],
        unique=False,
    )

    op.create_index(
        "ix_activities_organization_status",
        "activities",
        [
            "organization_id",
            "status",
        ],
        unique=False,
    )

    op.create_index(
        "ix_activities_organization_type",
        "activities",
        [
            "organization_id",
            "activity_type",
        ],
        unique=False,
    )

    op.create_index(
        op.f("ix_activities_status"),
        "activities",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_activities_status"),
        table_name="activities",
    )

    op.drop_index(
        "ix_activities_organization_type",
        table_name="activities",
    )

    op.drop_index(
        "ix_activities_organization_status",
        table_name="activities",
    )

    op.drop_index(
        "ix_activities_organization_opportunity_id",
        table_name="activities",
    )

    op.drop_index(
        "ix_activities_organization_lead_id",
        table_name="activities",
    )

    op.drop_index(
        op.f("ix_activities_organization_id"),
        table_name="activities",
    )

    op.drop_index(
        "ix_activities_organization_due_at",
        table_name="activities",
    )

    op.drop_index(
        "ix_activities_organization_contact_id",
        table_name="activities",
    )

    op.drop_index(
        "ix_activities_organization_company_id",
        table_name="activities",
    )

    op.drop_index(
        op.f("ix_activities_opportunity_id"),
        table_name="activities",
    )

    op.drop_index(
        op.f("ix_activities_lead_id"),
        table_name="activities",
    )

    op.drop_index(
        op.f("ix_activities_contact_id"),
        table_name="activities",
    )

    op.drop_index(
        op.f("ix_activities_company_id"),
        table_name="activities",
    )

    op.drop_index(
        op.f("ix_activities_activity_type"),
        table_name="activities",
    )

    op.drop_table(
        "activities",
    )