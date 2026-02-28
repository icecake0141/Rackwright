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

from sqlalchemy import select
from sqlalchemy.orm import Session

from rackwright.change_logging import change_log_context
from rackwright.models import Cabling, Device, PowerCabling

NETWORK_REQUIRED_COLUMNS = [
    "a_device",
    "a_port",
    "a_port_type",
    "b_device",
    "b_port",
    "b_port_type",
]
NETWORK_RECOMMENDED_COLUMNS = ["cable_type", "label"]
NETWORK_OPTIONAL_COLUMNS = ["length", "notes"]
NETWORK_EXPORT_COLUMNS = (
    NETWORK_REQUIRED_COLUMNS + NETWORK_RECOMMENDED_COLUMNS + NETWORK_OPTIONAL_COLUMNS
)

POWER_REQUIRED_COLUMNS = [
    "a_device",
    "a_port",
    "a_port_type",
    "b_device",
    "b_port",
    "b_port_type",
    "bank",
    "outlet",
]
POWER_RECOMMENDED_COLUMNS = ["cable_type", "label"]
POWER_OPTIONAL_COLUMNS = ["length", "notes"]
POWER_EXPORT_COLUMNS = (
    POWER_REQUIRED_COLUMNS + POWER_RECOMMENDED_COLUMNS + POWER_OPTIONAL_COLUMNS
)


@dataclass
class ParsedCsvRow:
    row_number: int
    values: dict[str, str]


def _normalize_text(value: str) -> str:
    return value.strip()


def _normalize_key_part(value: str) -> str:
    return _normalize_text(value).lower()


def _normalize_endpoint(device: str, port: str, port_type: str) -> tuple[str, str, str]:
    return (
        _normalize_key_part(device),
        _normalize_key_part(port),
        _normalize_key_part(port_type),
    )


def normalize_cabling_key(
    a_device: str,
    a_port: str,
    a_port_type: str,
    b_device: str,
    b_port: str,
    b_port_type: str,
) -> str:
    endpoint_a = _normalize_endpoint(a_device, a_port, a_port_type)
    endpoint_b = _normalize_endpoint(b_device, b_port, b_port_type)
    left, right = sorted([endpoint_a, endpoint_b])
    return f"{left[0]}::{left[1]}::{left[2]}|{right[0]}::{right[1]}::{right[2]}"


def normalize_power_cabling_key(
    a_device: str,
    a_port: str,
    a_port_type: str,
    b_device: str,
    b_port: str,
    b_port_type: str,
    bank: str,
    outlet: str,
) -> str:
    base = normalize_cabling_key(
        a_device, a_port, a_port_type, b_device, b_port, b_port_type
    )
    return f"{base}|{_normalize_key_part(bank)}|{_normalize_key_part(outlet)}"


def _parse_csv(csv_text: str, required_columns: list[str]) -> list[ParsedCsvRow]:
    reader = csv.DictReader(StringIO(csv_text))
    if reader.fieldnames is None:
        raise ValueError("CSV header is required")

    missing = [name for name in required_columns if name not in reader.fieldnames]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    rows: list[ParsedCsvRow] = []
    for row_number, row in enumerate(reader, start=2):
        normalized_row = {
            k: _normalize_text(v or "") for k, v in row.items() if k is not None
        }
        for column in required_columns:
            if not normalized_row.get(column):
                raise ValueError(
                    f"Row {row_number}: required column '{column}' is empty"
                )
        rows.append(ParsedCsvRow(row_number=row_number, values=normalized_row))
    return rows


def _project_device_names(session: Session, project_id: int) -> set[str]:
    statement = select(Device.name).where(Device.project_id == project_id)
    return {name for (name,) in session.execute(statement).all()}


def _ensure_placeholders(
    session: Session, project_id: int, device_names: set[str]
) -> None:
    if not device_names:
        return
    existing_names = _project_device_names(session, project_id)
    for name in sorted(device_names):
        if name in existing_names:
            continue
        session.add(
            Device(
                project_id=project_id,
                name=name,
                role="Other",
                rack_id=None,
            )
        )


def _ensure_power_placeholders(
    session: Session,
    project_id: int,
    parsed_rows: list[ParsedCsvRow],
    unknown_devices: set[str],
) -> None:
    if not unknown_devices:
        return
    existing_names = _project_device_names(session, project_id)
    pdu_names = {
        row.values["b_device"]
        for row in parsed_rows
        if row.values["b_device"] in unknown_devices
    }
    for name in sorted(unknown_devices):
        if name in existing_names:
            continue
        role = "PDU" if name in pdu_names else "Other"
        session.add(
            Device(
                project_id=project_id,
                name=name,
                role=role,
                rack_id=None,
            )
        )


def export_cabling_csv(session: Session, project_id: int) -> str:
    rows = (
        session.execute(
            select(Cabling).where(Cabling.project_id == project_id).order_by(Cabling.id)
        )
        .scalars()
        .all()
    )
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=NETWORK_EXPORT_COLUMNS)
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "a_device": row.a_device,
                "a_port": row.a_port,
                "a_port_type": row.a_port_type,
                "b_device": row.b_device,
                "b_port": row.b_port,
                "b_port_type": row.b_port_type,
                "cable_type": row.cable_type or "",
                "label": row.label or "",
                "length": row.length or "",
                "notes": row.notes or "",
            }
        )
    return output.getvalue()


def export_power_cabling_csv(session: Session, project_id: int) -> str:
    rows = (
        session.execute(
            select(PowerCabling)
            .where(PowerCabling.project_id == project_id)
            .order_by(PowerCabling.id)
        )
        .scalars()
        .all()
    )
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=POWER_EXPORT_COLUMNS)
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "a_device": row.a_device,
                "a_port": row.a_port,
                "a_port_type": row.a_port_type,
                "b_device": row.b_device,
                "b_port": row.b_port,
                "b_port_type": row.b_port_type,
                "bank": row.bank,
                "outlet": row.outlet,
                "cable_type": row.cable_type or "",
                "label": row.label or "",
                "length": row.length or "",
                "notes": row.notes or "",
            }
        )
    return output.getvalue()


def dry_run_cabling_import(
    session: Session, project_id: int, csv_text: str
) -> dict[str, object]:
    parsed_rows = _parse_csv(csv_text, NETWORK_REQUIRED_COLUMNS)
    existing_devices = _project_device_names(session, project_id)
    unknown_devices: set[str] = set()
    for row in parsed_rows:
        a_device = row.values["a_device"]
        b_device = row.values["b_device"]
        if a_device not in existing_devices:
            unknown_devices.add(a_device)
        if b_device not in existing_devices:
            unknown_devices.add(b_device)
    return {
        "rows": parsed_rows,
        "unknown_devices": sorted(unknown_devices),
    }


def dry_run_power_cabling_import(
    session: Session, project_id: int, csv_text: str
) -> dict[str, object]:
    parsed_rows = _parse_csv(csv_text, POWER_REQUIRED_COLUMNS)
    existing_devices = _project_device_names(session, project_id)
    unknown_devices: set[str] = set()
    for row in parsed_rows:
        a_device = row.values["a_device"]
        b_device = row.values["b_device"]
        if a_device not in existing_devices:
            unknown_devices.add(a_device)
        if b_device not in existing_devices:
            unknown_devices.add(b_device)
    return {
        "rows": parsed_rows,
        "unknown_devices": sorted(unknown_devices),
    }


def apply_cabling_import(
    session: Session,
    project_id: int,
    csv_text: str,
    file_name: str,
    *,
    create_placeholders: bool,
) -> dict[str, int]:
    dry_run_result = dry_run_cabling_import(session, project_id, csv_text)
    parsed_rows = dry_run_result["rows"]
    unknown_devices = set(dry_run_result["unknown_devices"])

    if unknown_devices and not create_placeholders:
        raise ValueError(
            "Unknown devices found; confirm placeholder creation before applying"
        )

    if create_placeholders:
        with change_log_context(source="csv_import", file=file_name, row=0):
            _ensure_placeholders(session, project_id, unknown_devices)
            session.flush()

    existing = {
        row.normalized_key: row
        for row in session.execute(
            select(Cabling).where(Cabling.project_id == project_id)
        )
        .scalars()
        .all()
    }

    updated = 0
    inserted = 0
    for parsed in parsed_rows:
        values = parsed.values
        normalized_key = normalize_cabling_key(
            values["a_device"],
            values["a_port"],
            values["a_port_type"],
            values["b_device"],
            values["b_port"],
            values["b_port_type"],
        )
        with change_log_context(
            source="csv_import", file=file_name, row=parsed.row_number
        ):
            current = existing.get(normalized_key)
            if current is None:
                current = Cabling(
                    project_id=project_id,
                    normalized_key=normalized_key,
                )
                session.add(current)
                existing[normalized_key] = current
                inserted += 1
            else:
                updated += 1

            current.a_device = values["a_device"]
            current.a_port = values["a_port"]
            current.a_port_type = values["a_port_type"]
            current.b_device = values["b_device"]
            current.b_port = values["b_port"]
            current.b_port_type = values["b_port_type"]
            current.cable_type = values.get("cable_type") or None
            current.label = values.get("label") or None
            current.length = values.get("length") or None
            current.notes = values.get("notes") or None
            session.flush()

    return {"inserted": inserted, "updated": updated, "unchanged": 0}


def apply_power_cabling_import(
    session: Session,
    project_id: int,
    csv_text: str,
    file_name: str,
    *,
    create_placeholders: bool,
) -> dict[str, int]:
    dry_run_result = dry_run_power_cabling_import(session, project_id, csv_text)
    parsed_rows = dry_run_result["rows"]
    unknown_devices = set(dry_run_result["unknown_devices"])

    if unknown_devices and not create_placeholders:
        raise ValueError(
            "Unknown devices found; confirm placeholder creation before applying"
        )

    if create_placeholders:
        with change_log_context(source="csv_import", file=file_name, row=0):
            _ensure_power_placeholders(
                session, project_id, parsed_rows, unknown_devices
            )
            session.flush()

    existing = {
        row.normalized_key: row
        for row in session.execute(
            select(PowerCabling).where(PowerCabling.project_id == project_id)
        )
        .scalars()
        .all()
    }

    updated = 0
    inserted = 0
    for parsed in parsed_rows:
        values = parsed.values
        normalized_key = normalize_power_cabling_key(
            values["a_device"],
            values["a_port"],
            values["a_port_type"],
            values["b_device"],
            values["b_port"],
            values["b_port_type"],
            values["bank"],
            values["outlet"],
        )
        with change_log_context(
            source="csv_import", file=file_name, row=parsed.row_number
        ):
            current = existing.get(normalized_key)
            if current is None:
                current = PowerCabling(
                    project_id=project_id,
                    normalized_key=normalized_key,
                )
                session.add(current)
                existing[normalized_key] = current
                inserted += 1
            else:
                updated += 1

            current.a_device = values["a_device"]
            current.a_port = values["a_port"]
            current.a_port_type = values["a_port_type"]
            current.b_device = values["b_device"]
            current.b_port = values["b_port"]
            current.b_port_type = values["b_port_type"]
            current.bank = values["bank"]
            current.outlet = values["outlet"]
            current.cable_type = values.get("cable_type") or None
            current.label = values.get("label") or None
            current.length = values.get("length") or None
            current.notes = values.get("notes") or None
            session.flush()

    return {"inserted": inserted, "updated": updated, "unchanged": 0}
