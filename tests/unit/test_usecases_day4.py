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


def test_bootstrap_zerostage_usecase_assigns_unique_name() -> None:
    _run_snippet(
        """
from rackwright.app.usecases import BootstrapZeroStageTemplateSetUseCase
from rackwright.core import TemplateSet

class FakeTemplateRepo:
    def __init__(self):
        self.items = [TemplateSet(name="ZeroStage Starter Pack")]

    def create(self, template_set):
        self.items.append(template_set)
        return template_set

    def get_by_name(self, name):
        for item in self.items:
            if item.name == name:
                return item
        return None

    def list_all(self):
        return list(self.items)

repo = FakeTemplateRepo()
created = BootstrapZeroStageTemplateSetUseCase(repo).execute()
assert created.name == "ZeroStage Starter Pack 2"
assert len(created.sections) == 8
"""
    )


def test_create_project_from_template_set_usecase_creates_snapshot() -> None:
    _run_snippet(
        """
from rackwright.app.dto import CreateProjectFromTemplateInput
from rackwright.app.usecases import CreateProjectFromTemplateSetUseCase
from rackwright.core import OutputTarget, TemplateSection, TemplateSet

class FakeTemplateRepo:
    def __init__(self):
        self.items = {}
        ts = TemplateSet(name="starter")
        ts.add_section(
            TemplateSection(
                target_type="Project",
                category="Network",
                section_order=1,
                output_targets=(OutputTarget.WORD,),
                applicable_roles=None,
                text="net",
            )
        )
        self.items[ts.name] = ts

    def create(self, template_set):
        self.items[template_set.name] = template_set
        return template_set

    def get_by_name(self, name):
        return self.items.get(name)

    def list_all(self):
        return list(self.items.values())

class FakeProjectRepo:
    def __init__(self):
        self.created = []

    def create(self, project):
        self.created.append(project)
        return project

class FakeSnapshotRepo:
    def __init__(self):
        self.calls = []

    def create_from_template(self, *, project, template_set):
        self.calls.append((project.name, template_set.name))

template_repo = FakeTemplateRepo()
project_repo = FakeProjectRepo()
snapshot_repo = FakeSnapshotRepo()
uc = CreateProjectFromTemplateSetUseCase(
    template_sets=template_repo,
    projects=project_repo,
    snapshots=snapshot_repo,
)
result = uc.execute(
    CreateProjectFromTemplateInput(
        template_set_name="starter",
        project_name="demo",
        owner="alice",
    )
)
assert result.name == "demo"
assert snapshot_repo.calls == [("demo", "starter")]
"""
    )


def test_create_project_from_template_set_raises_not_found() -> None:
    _run_snippet(
        """
from rackwright.app.dto import CreateProjectFromTemplateInput
from rackwright.app.usecases import CreateProjectFromTemplateSetUseCase
from rackwright.core import NotFoundError

class FakeTemplateRepo:
    def create(self, template_set):
        return template_set

    def get_by_name(self, name):
        return None

    def list_all(self):
        return []

class FakeProjectRepo:
    def create(self, project):
        return project

class FakeSnapshotRepo:
    def create_from_template(self, *, project, template_set):
        raise AssertionError("must not be called")

uc = CreateProjectFromTemplateSetUseCase(
    template_sets=FakeTemplateRepo(),
    projects=FakeProjectRepo(),
    snapshots=FakeSnapshotRepo(),
)
try:
    uc.execute(
        CreateProjectFromTemplateInput(
            template_set_name="missing",
            project_name="demo",
        )
    )
except NotFoundError:
    pass
else:
    raise SystemExit("expected NotFoundError")
"""
    )

