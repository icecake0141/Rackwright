"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_LICENSE = "SPDX-License-Identifier: Apache-2.0"
REQUIRED_LLM_ATTRIBUTION = "assistance of an AI (Large Language Model)"
SUPPORTED_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".css",
    ".html",
}
SCAN_LIMIT = 40


def _is_source_file(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_SUFFIXES


def _header_contains_requirements(path: Path) -> tuple[bool, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return False, "file is not valid UTF-8"

    header_text = "\n".join(lines[:SCAN_LIMIT])
    missing = []
    if REQUIRED_LICENSE not in header_text:
        missing.append("SPDX license identifier")
    if REQUIRED_LLM_ATTRIBUTION not in header_text:
        missing.append("LLM attribution")
    if missing:
        return False, ", ".join(missing)
    return True, ""


def main(argv: list[str]) -> int:
    failed = False
    for raw in argv[1:]:
        path = Path(raw)
        if not path.exists() or not path.is_file() or not _is_source_file(path):
            continue

        ok, reason = _header_contains_requirements(path)
        if not ok:
            print(f"{path}: missing required header content ({reason})")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
