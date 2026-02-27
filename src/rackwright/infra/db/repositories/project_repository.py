"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ....core import ConflictError, Project
from ..models import ProjectRecord


class SqlAlchemyProjectRepository:
    def __init__(self, session: Session):
        self._session = session

    def create(self, project: Project) -> Project:
        record = ProjectRecord(
            name=project.name,
            owner=project.owner,
            notes=project.notes,
            revision=project.revision,
            is_deleted=project.is_deleted,
        )
        try:
            self._session.add(record)
            self._session.flush()
        except IntegrityError as exc:
            self._session.rollback()
            raise ConflictError("project persistence conflict") from exc
        return Project(
            name=record.name,
            owner=record.owner,
            notes=record.notes,
            revision=record.revision,
            is_deleted=record.is_deleted,
        )

