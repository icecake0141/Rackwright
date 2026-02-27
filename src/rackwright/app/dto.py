"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateProjectFromTemplateInput:
    template_set_name: str
    project_name: str
    owner: str | None = None
    notes: str | None = None

