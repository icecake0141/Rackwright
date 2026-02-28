"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from rackwright.models import (
    Project,
    SectionApplicationRule,
    SectionSnapshot,
    TemplateSection,
    TemplateSet,
    TemplateSetSnapshot,
)


def _json_text(value: list[str] | dict[str, object] | None) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


def create_template_set(
    session: Session, name: str, description: str | None = None
) -> TemplateSet:
    template_set = TemplateSet(name=name, description=description)
    session.add(template_set)
    session.flush()
    return template_set


def update_template_set(
    session: Session, template_set_id: int, *, name: str, description: str | None
) -> TemplateSet:
    template_set = session.get(TemplateSet, template_set_id)
    if template_set is None:
        raise ValueError("Template set not found")
    template_set.name = name
    template_set.description = description
    session.flush()
    return template_set


def create_template_section(
    session: Session,
    template_set_id: int,
    *,
    target_type: str,
    category: str,
    section_order: int,
    output_targets: list[str],
    applicable_roles: list[str] | None,
    text: str,
) -> TemplateSection:
    section = TemplateSection(
        template_set_id=template_set_id,
        target_type=target_type,
        category=category,
        section_order=section_order,
        output_targets=_json_text(output_targets) or "[]",
        applicable_roles=_json_text(applicable_roles),
        text=text,
    )
    session.add(section)
    session.flush()
    return section


def update_template_section(
    session: Session,
    section_id: int,
    *,
    target_type: str,
    category: str,
    section_order: int,
    output_targets: list[str],
    applicable_roles: list[str] | None,
    text: str,
) -> TemplateSection:
    section = session.get(TemplateSection, section_id)
    if section is None:
        raise ValueError("Template section not found")
    section.target_type = target_type
    section.category = category
    section.section_order = section_order
    section.output_targets = _json_text(output_targets) or "[]"
    section.applicable_roles = _json_text(applicable_roles)
    section.text = text
    session.flush()
    return section


def create_project_from_template_set(
    session: Session,
    *,
    project_name: str,
    owner: str | None,
    notes: str | None,
    template_set_id: int,
) -> Project:
    template_set = session.get(TemplateSet, template_set_id)
    if template_set is None:
        raise ValueError("Template set not found")

    project = Project(name=project_name, owner=owner, notes=notes)
    session.add(project)
    session.flush()

    snapshot = TemplateSetSnapshot(
        project_id=project.id,
        source_template_set_id=str(template_set.id),
        name=template_set.name,
    )
    session.add(snapshot)
    session.flush()

    sections = (
        session.execute(
            select(TemplateSection)
            .where(TemplateSection.template_set_id == template_set_id)
            .order_by(TemplateSection.category, TemplateSection.section_order)
        )
        .scalars()
        .all()
    )

    for section in sections:
        section_snapshot = SectionSnapshot(
            template_set_snapshot_id=snapshot.id,
            target_type=section.target_type,
            category=section.category,
            section_order=section.section_order,
            output_targets=section.output_targets,
            applicable_roles=section.applicable_roles,
            text=section.text,
        )
        session.add(section_snapshot)
        session.flush()
        session.add(
            SectionApplicationRule(
                project_id=project.id,
                section_snapshot_id=section_snapshot.id,
                enabled=True,
                filters_json=None,
            )
        )

    session.flush()
    return project


def set_section_application_rule(
    session: Session,
    *,
    project_id: int,
    section_snapshot_id: int,
    enabled: bool,
    filters: dict[str, object] | None,
) -> SectionApplicationRule:
    rule = (
        session.execute(
            select(SectionApplicationRule).where(
                SectionApplicationRule.project_id == project_id,
                SectionApplicationRule.section_snapshot_id == section_snapshot_id,
            )
        )
        .scalars()
        .one_or_none()
    )

    if rule is None:
        rule = SectionApplicationRule(
            project_id=project_id,
            section_snapshot_id=section_snapshot_id,
            enabled=enabled,
            filters_json=_json_text(filters),
        )
        session.add(rule)
    else:
        rule.enabled = enabled
        rule.filters_json = _json_text(filters)

    session.flush()
    return rule
