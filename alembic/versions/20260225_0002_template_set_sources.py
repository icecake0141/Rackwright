"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260225_0002"
down_revision = "20260225_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "template_sets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "template_sections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "template_set_id",
            sa.Integer(),
            sa.ForeignKey("template_sets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("target_type", sa.String(length=32), nullable=False),
        sa.Column("category", sa.String(length=128), nullable=False),
        sa.Column("section_order", sa.Integer(), nullable=False),
        sa.Column("output_targets", sa.Text(), nullable=False),
        sa.Column("applicable_roles", sa.Text(), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "template_set_id",
            "category",
            "section_order",
            name="uq_template_sections_set_category_order",
        ),
    )
    op.create_index(
        "ix_template_sections_template_set_id", "template_sections", ["template_set_id"]
    )
    op.create_index(
        "ix_template_sections_order",
        "template_sections",
        ["template_set_id", "category", "section_order"],
    )


def downgrade() -> None:
    op.drop_index("ix_template_sections_order", table_name="template_sections")
    op.drop_index(
        "ix_template_sections_template_set_id", table_name="template_sections"
    )
    op.drop_table("template_sections")
    op.drop_table("template_sets")
