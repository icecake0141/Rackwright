"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _run_snippet(snippet: str) -> None:
    root = Path(__file__).resolve().parents[2]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root / "src")
    result = subprocess.run(
        [sys.executable, "-c", snippet],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"


def test_generate_artifacts_usecase_all_mode_outputs_three_targets() -> None:
    _run_snippet("""
import tempfile
from pathlib import Path

from rackwright.app.usecases import GenerateArtifactsInput, GenerateArtifactsUseCase
from rackwright.core import ArtifactMode
from rackwright.infra.exporters import (
    PlaintextExcelExporter,
    PlaintextImageExporter,
    PlaintextWordExporter,
)

with tempfile.TemporaryDirectory() as tmpdir:
    uc = GenerateArtifactsUseCase(
        exporters=(
            PlaintextWordExporter(),
            PlaintextExcelExporter(),
            PlaintextImageExporter(),
        )
    )
    result = uc.execute(
        GenerateArtifactsInput(
            project_name="demo",
            mode=ArtifactMode.ALL,
            sections=("s1", "s2"),
            out_dir=Path(tmpdir),
        )
    )
    assert len(result.outputs) == 3
""")


def test_generate_artifacts_usecase_filters_mode() -> None:
    _run_snippet("""
import tempfile
from pathlib import Path

from rackwright.app.usecases import GenerateArtifactsInput, GenerateArtifactsUseCase
from rackwright.core import ArtifactMode
from rackwright.infra.exporters import (
    PlaintextExcelExporter,
    PlaintextImageExporter,
    PlaintextWordExporter,
)

with tempfile.TemporaryDirectory() as tmpdir:
    uc = GenerateArtifactsUseCase(
        exporters=(
            PlaintextWordExporter(),
            PlaintextExcelExporter(),
            PlaintextImageExporter(),
        )
    )
    result = uc.execute(
        GenerateArtifactsInput(
            project_name="demo",
            mode=ArtifactMode.EXCEL,
            sections=("s1",),
            out_dir=Path(tmpdir),
        )
    )
    assert len(result.outputs) == 1
    assert result.outputs[0].artifact_type == "excel"
""")
