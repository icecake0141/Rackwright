"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import json

from sqlalchemy.orm import Session

from ....core import Project, TemplateSet
from ..models import (
    ProjectRecord,
    SectionApplicationRuleRecord,
    SectionSnapshotRecord,
    TemplateSetSnapshotRecord,
)


class SqlAlchemyProjectTemplateSnapshotRepository:
    def __init__(self, session: Session):
        self._session = session

    def create_from_template(self, *, project: Project, template_set: TemplateSet) -> None:
        project_record = self._session.query(ProjectRecord).filter_by(name=project.name).one()
        snapshot = TemplateSetSnapshotRecord(
            project_id=project_record.id,
            source_template_set_id=template_set.name,
            name=template_set.name,
        )
        self._session.add(snapshot)
        self._session.flush()

        for section in template_set.sorted_sections():
            section_snapshot = SectionSnapshotRecord(
                template_set_snapshot_id=snapshot.id,
                target_type=section.target_type,
                category=section.category,
                section_order=section.section_order,
                output_targets=json.dumps([item.value for item in section.output_targets]),
                applicable_roles=(
                    json.dumps(list(section.applicable_roles))
                    if section.applicable_roles is not None
                    else None
                ),
                text=section.text,
            )
            self._session.add(section_snapshot)
            self._session.flush()
            self._session.add(
                SectionApplicationRuleRecord(
                    project_id=project_record.id,
                    section_snapshot_id=section_snapshot.id,
                    enabled=True,
                    filters_json=None,
                )
            )

