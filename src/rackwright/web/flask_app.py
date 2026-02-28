"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from flask import Flask

from ..core import ConflictError, NotFoundError, ValidationError
from ..infra.db import create_all_tables, create_sqlite_engine
from .routes import register_routes


def create_app(database_url: str = "sqlite:///./rackwright_next.db") -> Flask:
    app = Flask(__name__)
    engine = create_sqlite_engine(database_url)
    create_all_tables(engine)
    app.config["RACKWRIGHT_ENGINE"] = engine
    register_routes(app)

    @app.errorhandler(ValidationError)
    def handle_validation_error(exc: ValidationError):
        return {"error": str(exc)}, 400

    @app.errorhandler(NotFoundError)
    def handle_not_found(exc: NotFoundError):
        return {"error": str(exc)}, 404

    @app.errorhandler(ConflictError)
    def handle_conflict(exc: ConflictError):
        return {"error": str(exc)}, 409

    return app
