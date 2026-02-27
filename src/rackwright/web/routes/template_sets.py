"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from flask import Blueprint, current_app, request
from sqlalchemy.orm import Session

from ...app.usecases.bootstrap_templates import BootstrapZeroStageTemplateSetUseCase
from ...infra.db.repositories import SqlAlchemyTemplateSetRepository

template_sets_bp = Blueprint("template_sets", __name__, url_prefix="/template-sets")


@template_sets_bp.get("")
def template_sets_list():
    engine = current_app.config["RACKWRIGHT_ENGINE"]
    with Session(engine) as session:
        repo = SqlAlchemyTemplateSetRepository(session)
        template_sets = repo.list_all()
    return {
        "items": [
            {
                "name": item.name,
                "description": item.description,
                "section_count": len(item.sections),
            }
            for item in template_sets
        ]
    }


@template_sets_bp.post("/bootstrap/zerostage")
def template_sets_bootstrap_zerostage():
    payload = request.get_json(silent=True) or {}
    base_name = payload.get("base_name", "ZeroStage Starter Pack")
    if not isinstance(base_name, str):
        return {"error": "base_name must be a string"}, 400

    engine = current_app.config["RACKWRIGHT_ENGINE"]
    with Session(engine) as session:
        usecase = BootstrapZeroStageTemplateSetUseCase(
            SqlAlchemyTemplateSetRepository(session)
        )
        created = usecase.execute(base_name=base_name)

    return {
        "name": created.name,
        "description": created.description,
        "section_count": len(created.sections),
    }, 201
