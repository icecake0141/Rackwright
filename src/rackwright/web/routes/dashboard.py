"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from flask import Blueprint

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
def dashboard():
    return {
        "service": "rackwright-next",
        "status": "ok",
    }

