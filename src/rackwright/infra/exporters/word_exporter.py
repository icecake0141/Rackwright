"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from pathlib import Path

from ...app.ports.exporters import ArtifactExportResult, ArtifactRenderInput


class PlaintextWordExporter:
    artifact_type = "word"

    def export(self, payload: ArtifactRenderInput, out_dir: Path) -> ArtifactExportResult:
        path = out_dir / f"{payload.project_name}_work_instruction.docx.txt"
        body = "\n".join(payload.sections)
        path.write_text(
            f"[word placeholder]\nproject={payload.project_name}\nmode={payload.mode}\n{body}\n",
            encoding="utf-8",
        )
        return ArtifactExportResult(artifact_type=self.artifact_type, path=path)

