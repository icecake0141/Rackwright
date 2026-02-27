"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class ArtifactRenderInput:
    project_name: str
    mode: str
    sections: tuple[str, ...]
    remarks: str | None = None


@dataclass(frozen=True)
class ArtifactExportResult:
    artifact_type: str
    path: Path


class ArtifactExporter(Protocol):
    artifact_type: str

    def export(self, payload: ArtifactRenderInput, out_dir: Path) -> ArtifactExportResult:
        """Render one artifact and return its output path."""

