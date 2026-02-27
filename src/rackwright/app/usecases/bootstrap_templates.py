"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from dataclasses import dataclass

from ...core import ConflictError, OutputTarget, TemplateSection, TemplateSet
from ..ports import TemplateSetRepository


@dataclass(frozen=True)
class _StarterSection:
    category: str
    section_order: int
    text: str


ZERO_STAGE_STARTER_SECTIONS = (
    _StarterSection(
        category="Preconditions",
        section_order=1,
        text="Confirm maintenance window, site access, and change approval for {{ project.name }}.",
    ),
    _StarterSection(
        category="Safety",
        section_order=1,
        text="Verify safety controls and escalation contacts before execution.",
    ),
    _StarterSection(
        category="Network",
        section_order=1,
        text="Apply network cabling work instruction and validate endpoint mapping.",
    ),
    _StarterSection(
        category="Power",
        section_order=1,
        text="Validate PDU bank/outlet assignments and required power path checks.",
    ),
    _StarterSection(
        category="Physical",
        section_order=1,
        text="Confirm rack/device placement, RU allocation, and orientation constraints.",
    ),
    _StarterSection(
        category="Cutover",
        section_order=1,
        text="Execute cutover sequence in approved order with service continuity checks.",
    ),
    _StarterSection(
        category="Rollback",
        section_order=1,
        text="If validation fails, execute rollback in reverse order and record evidence.",
    ),
    _StarterSection(
        category="PostCheck",
        section_order=1,
        text="Record post-work verification results and handover notes for operations.",
    ),
)

ZERO_STAGE_DESCRIPTION = (
    "Starter template pack for ZeroStage field execution documents "
    "(network/power/physical/cutover/rollback/post-check)."
)


class BootstrapZeroStageTemplateSetUseCase:
    def __init__(self, template_sets: TemplateSetRepository):
        self._template_sets = template_sets

    def execute(
        self, *, base_name: str = "ZeroStage Starter Pack", max_retries: int = 3
    ) -> TemplateSet:
        for _ in range(max_retries):
            name = self._next_available_name(base_name=base_name)
            template_set = TemplateSet(name=name, description=ZERO_STAGE_DESCRIPTION)
            for section in ZERO_STAGE_STARTER_SECTIONS:
                template_set.add_section(
                    TemplateSection(
                        target_type="Project",
                        category=section.category,
                        section_order=section.section_order,
                        output_targets=(OutputTarget.WORD, OutputTarget.EXCEL),
                        applicable_roles=None,
                        text=section.text,
                    )
                )
            try:
                return self._template_sets.create(template_set)
            except ConflictError:
                continue
        raise ConflictError("failed to bootstrap template set after retries")

    def _next_available_name(self, *, base_name: str) -> str:
        existing_names = {item.name for item in self._template_sets.list_all()}
        if base_name not in existing_names:
            return base_name
        suffix = 2
        while True:
            candidate = f"{base_name} {suffix}"
            if candidate not in existing_names:
                return candidate
            suffix += 1

