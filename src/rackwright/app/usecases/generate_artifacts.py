"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ...core import ArtifactMode, ValidationError
from ..ports.exporters import (
    ArtifactExporter,
    ArtifactExportResult,
    ArtifactRenderInput,
)


@dataclass(frozen=True)
class GenerateArtifactsInput:
    project_name: str
    mode: ArtifactMode
    sections: tuple[str, ...]
    out_dir: Path
    remarks: str | None = None


@dataclass(frozen=True)
class GenerateArtifactsResult:
    outputs: tuple[ArtifactExportResult, ...]


class GenerateArtifactsUseCase:
    def __init__(self, exporters: tuple[ArtifactExporter, ...]):
        if not exporters:
            raise ValidationError("at least one exporter is required")
        self._exporters = exporters

    def execute(self, request: GenerateArtifactsInput) -> GenerateArtifactsResult:
        request.out_dir.mkdir(parents=True, exist_ok=True)
        allowed = self._allowed_targets(request.mode)

        outputs: list[ArtifactExportResult] = []
        payload = ArtifactRenderInput(
            project_name=request.project_name,
            mode=request.mode.value,
            sections=request.sections,
            remarks=request.remarks,
        )
        for exporter in self._exporters:
            if exporter.artifact_type not in allowed:
                continue
            outputs.append(exporter.export(payload, request.out_dir))
        return GenerateArtifactsResult(outputs=tuple(outputs))

    @staticmethod
    def _allowed_targets(mode: ArtifactMode) -> set[str]:
        if mode == ArtifactMode.ALL:
            return {"word", "excel", "image"}
        return {mode.value}

