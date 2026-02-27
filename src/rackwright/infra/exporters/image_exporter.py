"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from pathlib import Path

from ...app.ports.exporters import ArtifactExportResult, ArtifactRenderInput


class PlaintextImageExporter:
    artifact_type = "image"

    def export(self, payload: ArtifactRenderInput, out_dir: Path) -> ArtifactExportResult:
        path = out_dir / f"{payload.project_name}_topology.svg.txt"
        path.write_text(
            (
                "[image placeholder]\n"
                f"project={payload.project_name}\n"
                f"mode={payload.mode}\n"
                f"sections={len(payload.sections)}\n"
            ),
            encoding="utf-8",
        )
        return ArtifactExportResult(artifact_type=self.artifact_type, path=path)

