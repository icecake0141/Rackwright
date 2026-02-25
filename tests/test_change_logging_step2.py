"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import json

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from rackwright.change_logging import change_log_context, register_change_logging_hook
from rackwright.models import Base, FieldChangeLog, Project


def _new_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    register_change_logging_hook(Session)
    return Session(engine)


def test_single_field_change_produces_exactly_one_log_entry() -> None:
    with _new_session() as session:
        project = Project(name="p1", owner="owner-a")
        session.add(project)
        session.commit()

        session.query(FieldChangeLog).delete()
        session.commit()

        project.owner = "owner-b"
        with change_log_context(source="web_edit"):
            session.flush()

        logs = session.query(FieldChangeLog).order_by(FieldChangeLog.id).all()
        assert len(logs) == 1
        assert logs[0].entity_type == "Project"
        assert logs[0].field_name == "owner"
        assert logs[0].before_value == "owner-a"
        assert logs[0].after_value == "owner-b"
        assert json.loads(logs[0].context)["source"] == "web_edit"


def test_context_supports_csv_import_metadata() -> None:
    with _new_session() as session:
        project = Project(name="p2", owner="owner-a")
        session.add(project)
        session.commit()
        session.query(FieldChangeLog).delete()
        session.commit()

        project.owner = "owner-csv"
        with change_log_context(source="csv_import", file="network.csv", row=12):
            session.flush()

        log = session.query(FieldChangeLog).one()
        payload = json.loads(log.context)
        assert payload["source"] == "csv_import"
        assert payload["file"] == "network.csv"
        assert payload["row"] == 12


def test_context_supports_generate_metadata() -> None:
    with _new_session() as session:
        project = Project(name="p3", owner="owner-a")
        session.add(project)
        session.commit()
        session.query(FieldChangeLog).delete()
        session.commit()

        project.owner = "owner-gen"
        with change_log_context(source="generate", mode="all", version=3):
            session.flush()

        log = session.query(FieldChangeLog).one()
        payload = json.loads(log.context)
        assert payload["source"] == "generate"
        assert payload["mode"] == "all"
        assert payload["version"] == 3
