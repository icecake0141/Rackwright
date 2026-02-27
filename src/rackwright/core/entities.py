"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .errors import ConflictError, ValidationError
from .value_objects import ArtifactMode, OutputTarget, normalize_name


@dataclass
class Project:
    name: str
    owner: str | None = None
    notes: str | None = None
    revision: int = 1
    is_deleted: bool = False

    def __post_init__(self) -> None:
        self.name = normalize_name(self.name, field_name="project.name")
        if self.owner is not None:
            self.owner = self.owner.strip() or None
        if self.notes is not None:
            self.notes = self.notes.strip() or None
        if self.revision < 1:
            raise ValidationError("project.revision must be >= 1")

    def rename(self, name: str) -> None:
        self.name = normalize_name(name, field_name="project.name")

    def bump_revision(self) -> None:
        self.revision += 1

    def soft_delete(self) -> None:
        self.is_deleted = True


@dataclass(frozen=True)
class TemplateSection:
    target_type: str
    category: str
    section_order: int
    output_targets: tuple[OutputTarget, ...]
    applicable_roles: tuple[str, ...] | None
    text: str

    def __post_init__(self) -> None:
        target_type = normalize_name(self.target_type, field_name="section.target_type")
        category = normalize_name(self.category, field_name="section.category")
        text = normalize_name(self.text, field_name="section.text")
        if self.section_order < 1:
            raise ValidationError("section.section_order must be >= 1")
        if not self.output_targets:
            raise ValidationError("section.output_targets must not be empty")
        if self.applicable_roles is not None and not self.applicable_roles:
            raise ValidationError(
                "section.applicable_roles must be None or non-empty tuple"
            )
        object.__setattr__(self, "target_type", target_type)
        object.__setattr__(self, "category", category)
        object.__setattr__(self, "text", text)

    @property
    def unique_key(self) -> tuple[str, int]:
        return (self.category, self.section_order)


@dataclass
class TemplateSet:
    name: str
    description: str | None = None
    sections: list[TemplateSection] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.name = normalize_name(self.name, field_name="template_set.name")
        if self.description is not None:
            self.description = self.description.strip() or None
        self._validate_duplicate_sections()

    def add_section(self, section: TemplateSection) -> None:
        if section.unique_key in {s.unique_key for s in self.sections}:
            raise ConflictError(
                "duplicate section key "
                f"(category={section.category}, order={section.section_order})"
            )
        self.sections.append(section)

    def sorted_sections(self) -> list[TemplateSection]:
        return sorted(
            self.sections, key=lambda item: (item.category, item.section_order)
        )

    def _validate_duplicate_sections(self) -> None:
        seen: set[tuple[str, int]] = set()
        for section in self.sections:
            key = section.unique_key
            if key in seen:
                raise ConflictError(
                    f"duplicate section key (category={key[0]}, order={key[1]})"
                )
            seen.add(key)


@dataclass
class ArtifactVersion:
    version_number: int
    mode: ArtifactMode
    fingerprint: str
    remarks: str | None = None
    success_word: bool = False
    success_excel: bool = False
    success_image: bool = False
    errors: list[dict[str, object]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.version_number < 1:
            raise ValidationError("artifact_version.version_number must be >= 1")
        self.fingerprint = normalize_name(
            self.fingerprint, field_name="artifact_version.fingerprint"
        )
        if self.remarks is not None:
            self.remarks = self.remarks.strip() or None

    def mark_success(self, target: OutputTarget) -> None:
        if target is OutputTarget.WORD:
            self.success_word = True
        elif target is OutputTarget.EXCEL:
            self.success_excel = True
        elif target is OutputTarget.IMAGE:
            self.success_image = True
