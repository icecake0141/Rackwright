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


def test_template_set_repository_create_and_query() -> None:
    _run_snippet("""
from rackwright.core import OutputTarget, TemplateSection, TemplateSet
from rackwright.infra.db import create_all_tables, create_sqlite_engine
from rackwright.infra.db.repositories import SqlAlchemyTemplateSetRepository
from sqlalchemy.orm import Session

engine = create_sqlite_engine("sqlite:///:memory:")
create_all_tables(engine)
with Session(engine) as session:
    repo = SqlAlchemyTemplateSetRepository(session)
    ts = TemplateSet(name="Starter", description="desc")
    ts.add_section(
        TemplateSection(
            target_type="Project",
            category="Network",
            section_order=1,
            output_targets=(OutputTarget.WORD, OutputTarget.EXCEL),
            applicable_roles=None,
            text="Check cabling",
        )
    )
    repo.create(ts)
    loaded = repo.get_by_name("Starter")
    assert loaded is not None
    assert loaded.name == "Starter"
    assert len(loaded.sections) == 1
    assert loaded.sections[0].output_targets[0].value == "word"
""")


def test_template_set_repository_name_conflict_maps_to_domain_error() -> None:
    _run_snippet("""
from rackwright.core import ConflictError, TemplateSet
from rackwright.infra.db import create_all_tables, create_sqlite_engine
from rackwright.infra.db.repositories import SqlAlchemyTemplateSetRepository
from sqlalchemy.orm import Session

engine = create_sqlite_engine("sqlite:///:memory:")
create_all_tables(engine)
with Session(engine) as session:
    repo = SqlAlchemyTemplateSetRepository(session)
    repo.create(TemplateSet(name="Same"))
    try:
        repo.create(TemplateSet(name="Same"))
    except ConflictError:
        pass
    else:
        raise SystemExit("expected ConflictError")
""")
