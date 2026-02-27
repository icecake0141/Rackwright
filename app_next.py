"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def create_app(database_url: str | None = None):
    src_dir = Path(__file__).resolve().parent / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from rackwright.web import create_app as create_next_app

    resolved_database_url = database_url or os.environ.get(
        "RACKWRIGHT_DATABASE_URL", "sqlite:///./rackwright_next.db"
    )
    return create_next_app(resolved_database_url)


if __name__ == "__main__":
    app = create_app()
    host = os.environ.get("RACKWRIGHT_HOST", "127.0.0.1")
    port = int(os.environ.get("RACKWRIGHT_PORT", "8010"))
    debug = os.environ.get("RACKWRIGHT_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)

