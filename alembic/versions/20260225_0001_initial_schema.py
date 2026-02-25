"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260225_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("owner", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "sites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("entry_procedure", sa.Text(), nullable=True),
        sa.Column("contact_info", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("project_id", "name", name="uq_sites_project_name"),
    )
    op.create_index("ix_sites_project_id", "sites", ["project_id"])

    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "site_id",
            sa.Integer(),
            sa.ForeignKey("sites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("site_id", "name", name="uq_rooms_site_name"),
    )
    op.create_index("ix_rooms_site_id", "rooms", ["site_id"])

    op.create_table(
        "rows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "room_id",
            sa.Integer(),
            sa.ForeignKey("rooms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("room_id", "name", name="uq_rows_room_name"),
    )
    op.create_index("ix_rows_room_id", "rows", ["room_id"])

    op.create_table(
        "racks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "row_id",
            sa.Integer(),
            sa.ForeignKey("rows.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("rack_height_u", sa.Integer(), nullable=False, server_default="42"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("project_id", "name", name="uq_racks_project_name"),
    )
    op.create_index("ix_racks_project_id", "racks", ["project_id"])
    op.create_index("ix_racks_row_id", "racks", ["row_id"])
    op.create_index("ix_racks_project_row", "racks", ["project_id", "row_id"])

    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "rack_id",
            sa.Integer(),
            sa.ForeignKey("racks.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False, server_default="Other"),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("serial", sa.String(length=255), nullable=True),
        sa.Column("power_watts", sa.Integer(), nullable=True),
        sa.Column("ru_start", sa.Integer(), nullable=True),
        sa.Column("ru_size", sa.Integer(), nullable=True),
        sa.Column("orientation", sa.String(length=32), nullable=True),
        sa.Column("device_vars", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("project_id", "name", name="uq_devices_project_name"),
    )
    op.create_index("ix_devices_project_id", "devices", ["project_id"])
    op.create_index("ix_devices_rack_id", "devices", ["rack_id"])
    op.create_index("ix_devices_project_rack", "devices", ["project_id", "rack_id"])

    op.create_table(
        "cablings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("a_device", sa.String(length=255), nullable=False),
        sa.Column("a_port", sa.String(length=255), nullable=False),
        sa.Column("a_port_type", sa.String(length=64), nullable=False),
        sa.Column("b_device", sa.String(length=255), nullable=False),
        sa.Column("b_port", sa.String(length=255), nullable=False),
        sa.Column("b_port_type", sa.String(length=64), nullable=False),
        sa.Column("cable_type", sa.String(length=64), nullable=True),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("length", sa.String(length=64), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("normalized_key", sa.String(length=1024), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "project_id", "normalized_key", name="uq_cablings_project_normalized_key"
        ),
    )
    op.create_index("ix_cablings_project_id", "cablings", ["project_id"])
    op.create_index(
        "ix_cablings_project_endpoint",
        "cablings",
        ["project_id", "a_device", "b_device"],
    )

    op.create_table(
        "power_cablings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("a_device", sa.String(length=255), nullable=False),
        sa.Column("a_port", sa.String(length=255), nullable=False),
        sa.Column("a_port_type", sa.String(length=64), nullable=False),
        sa.Column("b_device", sa.String(length=255), nullable=False),
        sa.Column("b_port", sa.String(length=255), nullable=False),
        sa.Column("b_port_type", sa.String(length=64), nullable=False),
        sa.Column("bank", sa.String(length=64), nullable=False),
        sa.Column("outlet", sa.String(length=64), nullable=False),
        sa.Column("cable_type", sa.String(length=64), nullable=True),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("length", sa.String(length=64), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("normalized_key", sa.String(length=1024), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "project_id",
            "normalized_key",
            name="uq_power_cablings_project_normalized_key",
        ),
    )
    op.create_index("ix_power_cablings_project_id", "power_cablings", ["project_id"])
    op.create_index(
        "ix_power_cablings_project_endpoint",
        "power_cablings",
        ["project_id", "a_device", "b_device"],
    )

    op.create_table(
        "template_set_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_template_set_id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "project_id",
            "source_template_set_id",
            name="uq_template_snapshot_project_source",
        ),
    )
    op.create_index(
        "ix_template_set_snapshots_project_id", "template_set_snapshots", ["project_id"]
    )

    op.create_table(
        "section_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "template_set_snapshot_id",
            sa.Integer(),
            sa.ForeignKey("template_set_snapshots.id", ondelete="CASCADE"),
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
    )
    op.create_index(
        "ix_section_snapshots_template_set_snapshot_id",
        "section_snapshots",
        ["template_set_snapshot_id"],
    )
    op.create_index(
        "ix_section_snapshots_order",
        "section_snapshots",
        ["template_set_snapshot_id", "category", "section_order"],
    )

    op.create_table(
        "section_application_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "section_snapshot_id",
            sa.Integer(),
            sa.ForeignKey("section_snapshots.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("filters_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "project_id", "section_snapshot_id", name="uq_section_rule_project_section"
        ),
    )
    op.create_index(
        "ix_section_application_rules_project_id",
        "section_application_rules",
        ["project_id"],
    )
    op.create_index(
        "ix_section_application_rules_section_snapshot_id",
        "section_application_rules",
        ["section_snapshot_id"],
    )

    op.create_table(
        "artifact_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("fingerprint", sa.String(length=512), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column(
            "success_word", sa.Boolean(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "success_excel", sa.Boolean(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "success_image", sa.Boolean(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column("errors_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "project_id", "fingerprint", name="uq_artifact_versions_project_fingerprint"
        ),
        sa.UniqueConstraint(
            "project_id", "version_number", name="uq_artifact_versions_project_version"
        ),
    )
    op.create_index(
        "ix_artifact_versions_project_id", "artifact_versions", ["project_id"]
    )
    op.create_index(
        "ix_artifact_versions_project_created",
        "artifact_versions",
        ["project_id", "created_at"],
    )

    op.create_table(
        "artifact_files",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "artifact_version_id",
            sa.Integer(),
            sa.ForeignKey("artifact_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("artifact_type", sa.String(length=32), nullable=False),
        sa.Column("relative_path", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "artifact_version_id",
            "artifact_type",
            "relative_path",
            name="uq_artifact_files_unique",
        ),
    )
    op.create_index(
        "ix_artifact_files_artifact_version_id",
        "artifact_files",
        ["artifact_version_id"],
    )

    op.create_table(
        "diff_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "from_version_id",
            sa.Integer(),
            sa.ForeignKey("artifact_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "to_version_id",
            sa.Integer(),
            sa.ForeignKey("artifact_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "project_id",
            "from_version_id",
            "to_version_id",
            name="uq_diff_reports_project_pair",
        ),
    )
    op.create_index("ix_diff_reports_project_id", "diff_reports", ["project_id"])
    op.create_index(
        "ix_diff_reports_from_version_id", "diff_reports", ["from_version_id"]
    )
    op.create_index("ix_diff_reports_to_version_id", "diff_reports", ["to_version_id"])

    op.create_table(
        "diff_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "diff_report_id",
            sa.Integer(),
            sa.ForeignKey("diff_reports.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("artifact_type", sa.String(length=32), nullable=False),
        sa.Column("location", sa.Text(), nullable=False),
        sa.Column("change_type", sa.String(length=32), nullable=False),
        sa.Column("before_value", sa.Text(), nullable=True),
        sa.Column("after_value", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_diff_items_diff_report_id", "diff_items", ["diff_report_id"])

    op.create_table(
        "field_change_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("field_name", sa.String(length=128), nullable=False),
        sa.Column("before_value", sa.Text(), nullable=True),
        sa.Column("after_value", sa.Text(), nullable=True),
        sa.Column("context", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_field_change_logs_project_id", "field_change_logs", ["project_id"]
    )
    op.create_index(
        "ix_field_change_logs_project_entity",
        "field_change_logs",
        ["project_id", "entity_type", "entity_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_field_change_logs_project_entity", table_name="field_change_logs")
    op.drop_index("ix_field_change_logs_project_id", table_name="field_change_logs")
    op.drop_table("field_change_logs")

    op.drop_index("ix_diff_items_diff_report_id", table_name="diff_items")
    op.drop_table("diff_items")

    op.drop_index("ix_diff_reports_to_version_id", table_name="diff_reports")
    op.drop_index("ix_diff_reports_from_version_id", table_name="diff_reports")
    op.drop_index("ix_diff_reports_project_id", table_name="diff_reports")
    op.drop_table("diff_reports")

    op.drop_index("ix_artifact_files_artifact_version_id", table_name="artifact_files")
    op.drop_table("artifact_files")

    op.drop_index(
        "ix_artifact_versions_project_created", table_name="artifact_versions"
    )
    op.drop_index("ix_artifact_versions_project_id", table_name="artifact_versions")
    op.drop_table("artifact_versions")

    op.drop_index(
        "ix_section_application_rules_section_snapshot_id",
        table_name="section_application_rules",
    )
    op.drop_index(
        "ix_section_application_rules_project_id",
        table_name="section_application_rules",
    )
    op.drop_table("section_application_rules")

    op.drop_index("ix_section_snapshots_order", table_name="section_snapshots")
    op.drop_index(
        "ix_section_snapshots_template_set_snapshot_id", table_name="section_snapshots"
    )
    op.drop_table("section_snapshots")

    op.drop_index(
        "ix_template_set_snapshots_project_id", table_name="template_set_snapshots"
    )
    op.drop_table("template_set_snapshots")

    op.drop_index("ix_power_cablings_project_endpoint", table_name="power_cablings")
    op.drop_index("ix_power_cablings_project_id", table_name="power_cablings")
    op.drop_table("power_cablings")

    op.drop_index("ix_cablings_project_endpoint", table_name="cablings")
    op.drop_index("ix_cablings_project_id", table_name="cablings")
    op.drop_table("cablings")

    op.drop_index("ix_devices_project_rack", table_name="devices")
    op.drop_index("ix_devices_rack_id", table_name="devices")
    op.drop_index("ix_devices_project_id", table_name="devices")
    op.drop_table("devices")

    op.drop_index("ix_racks_project_row", table_name="racks")
    op.drop_index("ix_racks_row_id", table_name="racks")
    op.drop_index("ix_racks_project_id", table_name="racks")
    op.drop_table("racks")

    op.drop_index("ix_rows_room_id", table_name="rows")
    op.drop_table("rows")

    op.drop_index("ix_rooms_site_id", table_name="rooms")
    op.drop_table("rooms")

    op.drop_index("ix_sites_project_id", table_name="sites")
    op.drop_table("sites")

    op.drop_table("projects")
