"""
align leads table with lead schema

Revision ID: 9038c98440d6
Revises: 381787521ae5
Create Date: 2026-08-27 08:38:59.746425
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9038c98440d6"
down_revision: Union[str, Sequence[str], None] = "381787521ae5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "leads",
        sa.Column(
            "title",
            sa.String(length=200),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE leads
        SET title = CASE
            WHEN first_name IS NOT NULL
                AND btrim(first_name) <> ''
                AND last_name IS NOT NULL
                AND btrim(last_name) <> ''
            THEN btrim(first_name) || ' ' || btrim(last_name)

            WHEN first_name IS NOT NULL
                AND btrim(first_name) <> ''
            THEN btrim(first_name)

            WHEN last_name IS NOT NULL
                AND btrim(last_name) <> ''
            THEN btrim(last_name)

            WHEN company_id IS NOT NULL
            THEN 'Lead ' || company_id::text

            WHEN contact_id IS NOT NULL
            THEN 'Lead ' || contact_id::text

            ELSE 'Untitled Lead'
        END
        WHERE title IS NULL
        """
    )

    op.alter_column(
        "leads",
        "title",
        existing_type=sa.String(length=200),
        nullable=False,
    )

    op.add_column(
        "leads",
        sa.Column(
            "company_name",
            sa.String(length=200),
            nullable=True,
        ),
    )

    op.add_column(
        "leads",
        sa.Column(
            "estimated_value",
            sa.Numeric(
                precision=18,
                scale=2,
            ),
            nullable=True,
        ),
    )

    op.add_column(
        "leads",
        sa.Column(
            "currency",
            sa.String(length=3),
            server_default=sa.text("'INR'"),
            nullable=False,
        ),
    )

    op.alter_column(
        "leads",
        "first_name",
        existing_type=sa.VARCHAR(length=100),
        nullable=True,
    )

    op.alter_column(
        "leads",
        "source",
        existing_type=sa.VARCHAR(length=32),
        type_=sa.String(length=100),
        nullable=True,
        server_default=None,
    )

    op.drop_index(
        op.f("ix_leads_organization_name"),
        table_name="leads",
    )

    op.drop_index(
        op.f("ix_leads_organization_source"),
        table_name="leads",
    )

    op.drop_index(
        op.f("ix_leads_source"),
        table_name="leads",
    )

    op.create_index(
        "ix_leads_organization_title",
        "leads",
        [
            "organization_id",
            "title",
        ],
        unique=False,
    )

    op.drop_column(
        "leads",
        "score",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.add_column(
        "leads",
        sa.Column(
            "score",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.drop_index(
        "ix_leads_organization_title",
        table_name="leads",
    )

    op.execute(
        """
        UPDATE leads
        SET first_name = 'Unknown'
        WHERE first_name IS NULL
        """
    )

    op.execute(
        """
        UPDATE leads
        SET source = 'manual'
        WHERE source IS NULL
        """
    )

    op.alter_column(
        "leads",
        "source",
        existing_type=sa.String(length=100),
        type_=sa.VARCHAR(length=32),
        nullable=False,
        server_default=sa.text("'manual'"),
    )

    op.alter_column(
        "leads",
        "first_name",
        existing_type=sa.VARCHAR(length=100),
        nullable=False,
    )

    op.create_index(
        op.f("ix_leads_source"),
        "leads",
        [
            "source",
        ],
        unique=False,
    )

    op.create_index(
        op.f("ix_leads_organization_source"),
        "leads",
        [
            "organization_id",
            "source",
        ],
        unique=False,
    )

    op.create_index(
        op.f("ix_leads_organization_name"),
        "leads",
        [
            "organization_id",
            "last_name",
            "first_name",
        ],
        unique=False,
    )

    op.drop_column(
        "leads",
        "currency",
    )

    op.drop_column(
        "leads",
        "estimated_value",
    )

    op.drop_column(
        "leads",
        "company_name",
    )

    op.drop_column(
        "leads",
        "title",
    )