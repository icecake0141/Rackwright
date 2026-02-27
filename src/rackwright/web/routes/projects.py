"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from flask import Blueprint, current_app, request
from sqlalchemy.orm import Session

from ...app.dto import CreateProjectFromTemplateInput
from ...app.usecases.create_project_from_template_set import (
    CreateProjectFromTemplateSetUseCase,
)
from ...core import DomainError
from ...infra.db.repositories import (
    SqlAlchemyProjectRepository,
    SqlAlchemyProjectTemplateSnapshotRepository,
    SqlAlchemyTemplateSetRepository,
)

projects_bp = Blueprint("projects", __name__, url_prefix="/projects")


@projects_bp.post("")
def create_project():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return {"error": "json body is required"}, 400

    template_set_name = payload.get("template_set_name")
    project_name = payload.get("project_name")
    owner = payload.get("owner")
    notes = payload.get("notes")

    if not isinstance(template_set_name, str) or not template_set_name.strip():
        return {"error": "template_set_name is required"}, 400
    if not isinstance(project_name, str) or not project_name.strip():
        return {"error": "project_name is required"}, 400
    if owner is not None and not isinstance(owner, str):
        return {"error": "owner must be a string or null"}, 400
    if notes is not None and not isinstance(notes, str):
        return {"error": "notes must be a string or null"}, 400

    engine = current_app.config["RACKWRIGHT_ENGINE"]
    with Session(engine) as session:
        usecase = CreateProjectFromTemplateSetUseCase(
            template_sets=SqlAlchemyTemplateSetRepository(session),
            projects=SqlAlchemyProjectRepository(session),
            snapshots=SqlAlchemyProjectTemplateSnapshotRepository(session),
        )
        try:
            created = usecase.execute(
                CreateProjectFromTemplateInput(
                    template_set_name=template_set_name,
                    project_name=project_name,
                    owner=owner,
                    notes=notes,
                )
            )
            session.commit()
        except DomainError:
            session.rollback()
            raise
    return {
        "name": created.name,
        "owner": created.owner,
        "notes": created.notes,
        "revision": created.revision,
    }, 201
