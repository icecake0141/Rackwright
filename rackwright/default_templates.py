"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from rackwright.models import TemplateSet
from rackwright.template_services import create_template_section, create_template_set


@dataclass(frozen=True)
class StarterSection:
    category: str
    section_order: int
    text: str


ZERO_STAGE_STARTER_SECTIONS = [
    StarterSection(
        category="Preconditions",
        section_order=1,
        text=(
            "Confirm maintenance window, site access, and change approval for {{ project.name }}."
        ),
    ),
    StarterSection(
        category="Safety",
        section_order=1,
        text=(
            "Verify safety controls and escalation contacts before execution."
        ),
    ),
    StarterSection(
        category="Network",
        section_order=1,
        text=(
            "Apply network cabling work instruction and validate endpoint mapping."
        ),
    ),
    StarterSection(
        category="Power",
        section_order=1,
        text=(
            "Validate PDU bank/outlet assignments and required power path checks."
        ),
    ),
    StarterSection(
        category="Physical",
        section_order=1,
        text=(
            "Confirm rack/device placement, RU allocation, and orientation constraints."
        ),
    ),
    StarterSection(
        category="Cutover",
        section_order=1,
        text=(
            "Execute cutover sequence in approved order with service continuity checks."
        ),
    ),
    StarterSection(
        category="Rollback",
        section_order=1,
        text=(
            "If validation fails, execute rollback in reverse order and record evidence."
        ),
    ),
    StarterSection(
        category="PostCheck",
        section_order=1,
        text=(
            "Record post-work verification results and handover notes for operations."
        ),
    ),
]


def _next_available_template_set_name(session: Session, base_name: str) -> str:
    existing_names = set(
        session.execute(select(TemplateSet.name).where(TemplateSet.name.like(f"{base_name}%")))
        .scalars()
        .all()
    )
    if base_name not in existing_names:
        return base_name

    suffix = 2
    while True:
        candidate = f"{base_name} {suffix}"
        if candidate not in existing_names:
            return candidate
        suffix += 1


def create_zerostage_starter_template_set(
    session: Session,
    *,
    base_name: str = "ZeroStage Starter Pack",
) -> TemplateSet:
    template_set = create_template_set(
        session,
        name=_next_available_template_set_name(session, base_name),
        description=(
            "Starter template pack for ZeroStage field execution documents "
            "(network/power/physical/cutover/rollback/post-check)."
        ),
    )
    for section in ZERO_STAGE_STARTER_SECTIONS:
        create_template_section(
            session,
            template_set.id,
            target_type="Project",
            category=section.category,
            section_order=section.section_order,
            output_targets=["word", "excel"],
            applicable_roles=None,
            text=section.text,
        )
    session.flush()
    return template_set
