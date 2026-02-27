"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from flask import Flask

from .dashboard import dashboard_bp
from .projects import projects_bp
from .template_sets import template_sets_bp


def register_routes(app: Flask) -> None:
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(template_sets_bp)
    app.register_blueprint(projects_bp)

