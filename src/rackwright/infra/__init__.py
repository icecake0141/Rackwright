"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

__all__ = ["create_all_tables", "create_session_factory", "create_sqlite_engine"]


def create_sqlite_engine(database_url: str):
    from .db import create_sqlite_engine as _create_sqlite_engine

    return _create_sqlite_engine(database_url)


def create_session_factory(engine):
    from .db import create_session_factory as _create_session_factory

    return _create_session_factory(engine)


def create_all_tables(engine) -> None:
    from .db import create_all_tables as _create_all_tables

    _create_all_tables(engine)
