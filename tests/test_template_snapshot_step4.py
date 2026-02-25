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

from rackwright.models import (
    Base,
    SectionApplicationRule,
    SectionSnapshot,
    TemplateSection,
)
from rackwright.template_services import (
    create_project_from_template_set,
    create_template_section,
    create_template_set,
    set_section_application_rule,
)


def _new_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(engine)


def test_project_creation_snapshots_template_sections_and_keeps_json_text() -> None:
    with _new_session() as session:
        template_set = create_template_set(session, "Core", "desc")
        create_template_section(
            session,
            template_set.id,
            target_type="Project",
            category="General",
            section_order=1,
            output_targets=["word", "excel"],
            applicable_roles=["PDU", "Switch"],
            text="section-body",
        )
        session.commit()

        project = create_project_from_template_set(
            session,
            project_name="proj-1",
            owner="owner",
            notes="notes",
            template_set_id=template_set.id,
        )
        session.commit()

        snapshots = session.query(SectionSnapshot).all()
        assert len(snapshots) == 1
        assert json.loads(snapshots[0].output_targets) == ["word", "excel"]
        assert json.loads(snapshots[0].applicable_roles) == ["PDU", "Switch"]

        rules = (
            session.query(SectionApplicationRule)
            .filter(SectionApplicationRule.project_id == project.id)
            .all()
        )
        assert len(rules) == 1
        assert rules[0].enabled is True
        assert rules[0].filters_json is None


def test_snapshot_is_immutable_after_source_template_edit() -> None:
    with _new_session() as session:
        template_set = create_template_set(session, "Core2", None)
        section = create_template_section(
            session,
            template_set.id,
            target_type="Rack",
            category="Racks",
            section_order=2,
            output_targets=["word"],
            applicable_roles=None,
            text="before",
        )
        session.commit()

        create_project_from_template_set(
            session,
            project_name="proj-2",
            owner=None,
            notes=None,
            template_set_id=template_set.id,
        )
        session.commit()

        section.text = "after"
        session.commit()

        snapshot = session.query(SectionSnapshot).one()
        assert snapshot.text == "before"


def test_project_side_section_rule_update() -> None:
    with _new_session() as session:
        template_set = create_template_set(session, "Core3", None)
        create_template_section(
            session,
            template_set.id,
            target_type="Device",
            category="Devices",
            section_order=1,
            output_targets=["excel"],
            applicable_roles=["Server"],
            text="device",
        )
        session.commit()

        project = create_project_from_template_set(
            session,
            project_name="proj-3",
            owner=None,
            notes=None,
            template_set_id=template_set.id,
        )
        session.commit()

        section_snapshot = session.query(SectionSnapshot).one()
        rule = set_section_application_rule(
            session,
            project_id=project.id,
            section_snapshot_id=section_snapshot.id,
            enabled=False,
            filters={"rack_scope": ["rack-a"], "role": ["Server"]},
        )
        session.commit()

        assert rule.enabled is False
        assert json.loads(rule.filters_json) == {
            "rack_scope": ["rack-a"],
            "role": ["Server"],
        }
        template_source = session.query(TemplateSection).one()
        assert isinstance(template_source.output_targets, str)
