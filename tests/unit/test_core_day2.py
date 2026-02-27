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


def test_template_set_rejects_duplicate_sections() -> None:
    _run_snippet(
        """
from rackwright.core import ConflictError, OutputTarget, TemplateSection, TemplateSet

ts = TemplateSet(name="ZeroStage")
ts.add_section(
    TemplateSection(
        target_type="Project",
        category="Network",
        section_order=1,
        output_targets=(OutputTarget.WORD, OutputTarget.EXCEL),
        applicable_roles=None,
        text="First section",
    )
)
try:
    ts.add_section(
        TemplateSection(
            target_type="Project",
            category="Network",
            section_order=1,
            output_targets=(OutputTarget.WORD,),
            applicable_roles=None,
            text="Duplicate section",
        )
    )
except ConflictError:
    pass
else:
    raise SystemExit("expected ConflictError")
"""
    )


def test_project_validation_and_revision_bump() -> None:
    _run_snippet(
        """
from rackwright.core import Project, ValidationError

project = Project(name="  demo  ", owner="  alice  ")
assert project.name == "demo"
assert project.owner == "alice"
assert project.revision == 1
project.bump_revision()
assert project.revision == 2

try:
    Project(name="   ")
except ValidationError:
    pass
else:
    raise SystemExit("expected ValidationError")
"""
    )


def test_artifact_version_marks_success_flags() -> None:
    _run_snippet(
        """
from rackwright.core import ArtifactMode, ArtifactVersion, OutputTarget

version = ArtifactVersion(version_number=1, mode=ArtifactMode.ALL, fingerprint="abc")
version.mark_success(OutputTarget.WORD)
version.mark_success(OutputTarget.EXCEL)
assert version.success_word is True
assert version.success_excel is True
assert version.success_image is False
"""
    )
