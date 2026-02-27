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


def test_web_bootstrap_and_create_project_flow() -> None:
    _run_snippet(
        """
from rackwright.web import create_app

app = create_app("sqlite:///:memory:")
app.testing = True
client = app.test_client()

health = client.get("/")
assert health.status_code == 200
assert health.get_json()["status"] == "ok"

boot = client.post("/template-sets/bootstrap/zerostage", json={})
assert boot.status_code == 201
assert boot.get_json()["name"].startswith("ZeroStage Starter Pack")

created = client.post(
    "/projects",
    json={
        "template_set_name": boot.get_json()["name"],
        "project_name": "demo-project",
        "owner": "alice",
    },
)
assert created.status_code == 201
assert created.get_json()["name"] == "demo-project"
"""
    )


def test_web_create_project_returns_404_for_missing_template() -> None:
    _run_snippet(
        """
from rackwright.web import create_app

app = create_app("sqlite:///:memory:")
app.testing = True
client = app.test_client()

response = client.post(
    "/projects",
    json={"template_set_name": "missing", "project_name": "demo"},
)
assert response.status_code == 404
"""
    )
