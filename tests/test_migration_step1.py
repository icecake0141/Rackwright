"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from alembic import command


@pytest.fixture()
def alembic_config(tmp_path: Path) -> Config:
    db_path = tmp_path / "rackwright_test.db"
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    return cfg


def test_migration_upgrade_and_downgrade(alembic_config: Config) -> None:
    command.upgrade(alembic_config, "head")

    engine = create_engine(alembic_config.get_main_option("sqlalchemy.url"))
    inspector = inspect(engine)
    expected_tables = {
        "projects",
        "sites",
        "rooms",
        "rows",
        "racks",
        "devices",
        "cablings",
        "power_cablings",
        "template_sets",
        "template_sections",
        "template_set_snapshots",
        "section_snapshots",
        "section_application_rules",
        "artifact_versions",
        "artifact_files",
        "diff_reports",
        "diff_items",
        "field_change_logs",
        "alembic_version",
    }
    assert expected_tables.issubset(set(inspector.get_table_names()))

    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO projects (name, owner, notes, revision, is_deleted, created_at, updated_at) "
                "VALUES ('p1', 'o', 'n', 1, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO racks (project_id, row_id, name, rack_height_u, created_at, updated_at) "
                "VALUES (1, NULL, 'r1', 42, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO devices (project_id, rack_id, name, role, created_at, updated_at) "
                "VALUES (1, 1, 'd1', 'Other', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            )
        )

    with pytest.raises(Exception):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO racks (project_id, row_id, name, rack_height_u, created_at, updated_at) "
                    "VALUES (1, NULL, 'r1', 42, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                )
            )

    with pytest.raises(Exception):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO devices (project_id, rack_id, name, role, created_at, updated_at) "
                    "VALUES (1, 1, 'd1', 'Other', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                )
            )

    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO cablings ("
                "project_id, a_device, a_port, a_port_type, b_device, b_port, b_port_type, normalized_key, created_at, updated_at"
                ") VALUES (1, 'd1', 'p1', 'dcim.interface', 'd2', 'p2', 'dcim.interface', 'k1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            )
        )

    with pytest.raises(Exception):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO cablings ("
                    "project_id, a_device, a_port, a_port_type, b_device, b_port, b_port_type, normalized_key, created_at, updated_at"
                    ") VALUES (1, 'd2', 'p2', 'dcim.interface', 'd1', 'p1', 'dcim.interface', 'k1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                )
            )

    command.downgrade(alembic_config, "base")
    inspector_after = inspect(engine)
    assert inspector_after.get_table_names() == ["alembic_version"]
