"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO

from ...core import ValidationError

NETWORK_REQUIRED_COLUMNS = (
    "a_device",
    "a_port",
    "a_port_type",
    "b_device",
    "b_port",
    "b_port_type",
)
NETWORK_OPTIONAL_COLUMNS = ("cable_type", "label", "length", "notes")


@dataclass(frozen=True)
class ParsedCsvRow:
    row_number: int
    values: dict[str, str]


def parse_network_cabling_csv(csv_text: str) -> tuple[ParsedCsvRow, ...]:
    reader = csv.DictReader(StringIO(csv_text))
    if reader.fieldnames is None:
        raise ValidationError("CSV header is required")

    missing = [col for col in NETWORK_REQUIRED_COLUMNS if col not in reader.fieldnames]
    if missing:
        raise ValidationError(f"Missing required columns: {', '.join(missing)}")

    rows: list[ParsedCsvRow] = []
    for row_number, row in enumerate(reader, start=2):
        normalized = {
            key: (value.strip() if value is not None else "")
            for key, value in row.items()
            if key is not None
        }
        for column in NETWORK_REQUIRED_COLUMNS:
            if not normalized.get(column):
                raise ValidationError(
                    f"Row {row_number}: required column '{column}' is empty"
                )
        rows.append(ParsedCsvRow(row_number=row_number, values=normalized))
    return tuple(rows)

