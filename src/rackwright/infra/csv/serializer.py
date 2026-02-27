"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import csv
from io import StringIO

from .parser import NETWORK_OPTIONAL_COLUMNS, NETWORK_REQUIRED_COLUMNS


def serialize_network_cabling_csv(rows: tuple[dict[str, str], ...]) -> str:
    columns = NETWORK_REQUIRED_COLUMNS + NETWORK_OPTIONAL_COLUMNS
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(column, "") for column in columns})
    return output.getvalue()
