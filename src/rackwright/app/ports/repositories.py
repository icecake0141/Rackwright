"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from typing import Protocol

from ...core import Project, TemplateSet


class TemplateSetRepository(Protocol):
    def create(self, template_set: TemplateSet) -> TemplateSet:
        """Persist a new template set or raise ConflictError."""

    def get_by_name(self, name: str) -> TemplateSet | None:
        """Return one template set by unique name."""

    def list_all(self) -> list[TemplateSet]:
        """Return template sets ordered by name."""


class ProjectRepository(Protocol):
    def create(self, project: Project) -> Project:
        """Persist and return a project."""


class ProjectTemplateSnapshotRepository(Protocol):
    def create_from_template(
        self, *, project: Project, template_set: TemplateSet
    ) -> None:
        """Create snapshot/rule records derived from template set."""
