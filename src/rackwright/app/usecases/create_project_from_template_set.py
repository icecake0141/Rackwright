"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from ...core import NotFoundError, Project
from ..dto import CreateProjectFromTemplateInput
from ..ports import (
    ProjectRepository,
    ProjectTemplateSnapshotRepository,
    TemplateSetRepository,
)


class CreateProjectFromTemplateSetUseCase:
    def __init__(
        self,
        template_sets: TemplateSetRepository,
        projects: ProjectRepository,
        snapshots: ProjectTemplateSnapshotRepository,
    ):
        self._template_sets = template_sets
        self._projects = projects
        self._snapshots = snapshots

    def execute(self, request: CreateProjectFromTemplateInput) -> Project:
        template_set = self._template_sets.get_by_name(request.template_set_name)
        if template_set is None:
            raise NotFoundError(f"template set not found: {request.template_set_name}")

        created = self._projects.create(
            Project(
                name=request.project_name,
                owner=request.owner,
                notes=request.notes,
            )
        )
        self._snapshots.create_from_template(project=created, template_set=template_set)
        return created
