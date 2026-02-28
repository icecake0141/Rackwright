"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ....core import ConflictError, OutputTarget, TemplateSection, TemplateSet
from ...db.models import TemplateSectionRecord, TemplateSetRecord


class SqlAlchemyTemplateSetRepository:
    def __init__(self, session: Session):
        self._session = session

    def create(self, template_set: TemplateSet) -> TemplateSet:
        record = TemplateSetRecord(
            name=template_set.name, description=template_set.description
        )
        try:
            self._session.add(record)
            self._session.flush()

            for section in template_set.sections:
                section_record = TemplateSectionRecord(
                    template_set_id=record.id,
                    target_type=section.target_type,
                    category=section.category,
                    section_order=section.section_order,
                    output_targets=json.dumps(
                        [target.value for target in section.output_targets]
                    ),
                    applicable_roles=(
                        json.dumps(list(section.applicable_roles))
                        if section.applicable_roles is not None
                        else None
                    ),
                    text=section.text,
                )
                self._session.add(section_record)
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise ConflictError("template set persistence conflict") from exc
        return self._to_entity(record)

    def get_by_name(self, name: str) -> TemplateSet | None:
        record = (
            self._session.execute(
                select(TemplateSetRecord).where(TemplateSetRecord.name == name)
            )
            .scalars()
            .one_or_none()
        )
        if record is None:
            return None
        return self._to_entity(record)

    def list_all(self) -> list[TemplateSet]:
        records = (
            self._session.execute(
                select(TemplateSetRecord).order_by(TemplateSetRecord.name)
            )
            .scalars()
            .all()
        )
        return [self._to_entity(item) for item in records]

    @staticmethod
    def _to_entity(record: TemplateSetRecord) -> TemplateSet:
        sections = sorted(
            record.sections,
            key=lambda item: (item.category, item.section_order),
        )
        return TemplateSet(
            name=record.name,
            description=record.description,
            sections=[
                SqlAlchemyTemplateSetRepository._to_section(item) for item in sections
            ],
        )

    @staticmethod
    def _to_section(record: TemplateSectionRecord) -> TemplateSection:
        output_targets_raw = json.loads(record.output_targets)
        output_targets = tuple(OutputTarget(item) for item in output_targets_raw)
        applicable_roles = (
            tuple(json.loads(record.applicable_roles))
            if record.applicable_roles is not None
            else None
        )
        return TemplateSection(
            target_type=record.target_type,
            category=record.category,
            section_order=record.section_order,
            output_targets=output_targets,
            applicable_roles=applicable_roles,
            text=record.text,
        )
