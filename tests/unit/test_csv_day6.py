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


def test_parse_network_cabling_csv_success() -> None:
    _run_snippet(
        """
from rackwright.infra.csv import parse_network_cabling_csv

rows = parse_network_cabling_csv(
    "a_device,a_port,a_port_type,b_device,b_port,b_port_type\\n"
    "sw1,xe-0/0/0,if,sv1,eth0,if\\n"
)
assert len(rows) == 1
assert rows[0].values["a_device"] == "sw1"
"""
    )


def test_serialize_network_cabling_csv_contains_header() -> None:
    _run_snippet(
        """
from rackwright.infra.csv import serialize_network_cabling_csv

text = serialize_network_cabling_csv(
    (
        {
            "a_device": "sw1",
            "a_port": "xe-0/0/0",
            "a_port_type": "if",
            "b_device": "sv1",
            "b_port": "eth0",
            "b_port_type": "if",
        },
    )
)
assert text.startswith("a_device,a_port,a_port_type,b_device,b_port,b_port_type")
"""
    )

