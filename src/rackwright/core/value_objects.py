"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from enum import Enum

from .errors import ValidationError


class ArtifactMode(str, Enum):
    ALL = "all"
    WORD = "word"
    EXCEL = "excel"
    IMAGE = "image"


class OutputTarget(str, Enum):
    WORD = "word"
    EXCEL = "excel"
    IMAGE = "image"


def normalize_name(value: str, *, field_name: str = "name") -> str:
    normalized = value.strip()
    if not normalized:
        raise ValidationError(f"{field_name} is required")
    return normalized
