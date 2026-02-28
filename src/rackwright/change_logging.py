"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from sqlalchemy import event, select
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import Session

from rackwright.models import (
    ArtifactFile,
    Base,
    FieldChangeLog,
    Project,
    Room,
    Row,
    SectionSnapshot,
    Site,
)

_change_context: ContextVar[dict[str, Any]] = ContextVar(
    "rackwright_change_context", default={"source": "web_edit"}
)

IGNORED_FIELDS = {"id", "created_at", "updated_at"}


@contextmanager
def change_log_context(**kwargs: Any):
    current = dict(_change_context.get())
    current.update(kwargs)
    token = _change_context.set(current)
    try:
        yield
    finally:
        _change_context.reset(token)


def _stringify(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _project_id_for(obj: Any) -> int | None:
    if isinstance(obj, Project):
        return obj.id
    if hasattr(obj, "project_id"):
        return getattr(obj, "project_id")
    if isinstance(obj, Site):
        return obj.project_id
    if isinstance(obj, Room) and obj.site is not None:
        return obj.site.project_id
    if isinstance(obj, Row) and obj.room is not None and obj.room.site is not None:
        return obj.room.site.project_id
    if isinstance(obj, SectionSnapshot) and obj.template_set_snapshot is not None:
        return obj.template_set_snapshot.project_id
    if isinstance(obj, ArtifactFile) and obj.artifact_version is not None:
        return obj.artifact_version.project_id
    if hasattr(obj, "diff_report") and obj.diff_report is not None:
        return getattr(obj.diff_report, "project_id", None)
    return None


def _load_db_scalar_value(session: Session, obj: Any, field_name: str) -> Any:
    state = sa_inspect(obj)
    if state.identity is None:
        return None
    pk_col = state.mapper.primary_key[0]
    pk_value = state.identity[0]
    table = state.mapper.local_table
    statement = select(table.c[field_name]).where(pk_col == pk_value)
    return session.execute(statement).scalar_one_or_none()


def _iter_scalar_field_changes(session: Session, obj: Any, operation: str):
    state = sa_inspect(obj)
    for column_attr in state.mapper.column_attrs:
        field_name = column_attr.key
        if field_name in IGNORED_FIELDS:
            continue
        history = state.attrs[field_name].history
        if operation == "new":
            before_value = None
            after_value = getattr(obj, field_name)
            if after_value is None:
                continue
        elif operation == "deleted":
            before_value = getattr(obj, field_name)
            after_value = None
            if before_value is None:
                continue
        else:
            if not history.has_changes():
                continue
            if history.deleted:
                before_value = history.deleted[0]
            else:
                before_value = _load_db_scalar_value(session, obj, field_name)
            if history.added:
                after_value = history.added[0]
            else:
                after_value = getattr(obj, field_name)
            if before_value == after_value:
                continue
        yield field_name, _stringify(before_value), _stringify(after_value)


def _entity_type(obj: Any) -> str:
    return obj.__class__.__name__


def _context_payload() -> str:
    return json.dumps(_change_context.get(), ensure_ascii=False)


def _is_tracked_model(obj: Any) -> bool:
    if isinstance(obj, FieldChangeLog):
        return False
    return isinstance(obj, Base)


def register_change_logging_hook(session_cls: type[Session] = Session) -> None:
    if getattr(session_cls, "_rackwright_change_logging_registered", False):
        return

    @event.listens_for(session_cls, "before_flush")
    def _before_flush(session: Session, flush_context, instances) -> None:
        if session.info.get("_change_logging_in_progress", False):
            return

        session.info["_change_logging_in_progress"] = True
        try:
            for obj in session.new:
                if not _is_tracked_model(obj):
                    continue
                project_id = _project_id_for(obj)
                if project_id is None:
                    continue
                for field_name, before_value, after_value in _iter_scalar_field_changes(
                    session, obj, "new"
                ):
                    session.add(
                        FieldChangeLog(
                            project_id=project_id,
                            entity_type=_entity_type(obj),
                            entity_id=getattr(obj, "id", None),
                            field_name=field_name,
                            before_value=before_value,
                            after_value=after_value,
                            context=_context_payload(),
                        )
                    )

            for obj in session.dirty:
                if not _is_tracked_model(obj):
                    continue
                project_id = _project_id_for(obj)
                if project_id is None:
                    continue
                for field_name, before_value, after_value in _iter_scalar_field_changes(
                    session, obj, "dirty"
                ):
                    session.add(
                        FieldChangeLog(
                            project_id=project_id,
                            entity_type=_entity_type(obj),
                            entity_id=getattr(obj, "id", None),
                            field_name=field_name,
                            before_value=before_value,
                            after_value=after_value,
                            context=_context_payload(),
                        )
                    )

            for obj in session.deleted:
                if not _is_tracked_model(obj):
                    continue
                project_id = _project_id_for(obj)
                if project_id is None:
                    continue
                for field_name, before_value, after_value in _iter_scalar_field_changes(
                    session, obj, "deleted"
                ):
                    session.add(
                        FieldChangeLog(
                            project_id=project_id,
                            entity_type=_entity_type(obj),
                            entity_id=getattr(obj, "id", None),
                            field_name=field_name,
                            before_value=before_value,
                            after_value=after_value,
                            context=_context_payload(),
                        )
                    )
        finally:
            session.info["_change_logging_in_progress"] = False

    setattr(session_cls, "_rackwright_change_logging_registered", True)
