"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from rackwright.models import Cabling, Device, PowerCabling, Rack


@dataclass(frozen=True)
class DeviceView:
    id: int
    name: str
    role: str
    rack_id: int | None
    ru_start: int | None
    ru_size: int | None
    orientation: str | None
    model: str | None
    serial: str | None
    power_watts: int | None


@dataclass(frozen=True)
class CablingView:
    id: int
    a_device: str
    a_port: str
    a_port_type: str
    b_device: str
    b_port: str
    b_port_type: str
    cable_type: str | None
    label: str | None
    length: str | None
    notes: str | None
    normalized_key: str


def devices_in_rack(session: Session, rack_id: int) -> list[DeviceView]:
    rack = session.get(Rack, rack_id)
    if rack is None:
        return []

    rows = (
        session.execute(
            select(Device)
            .where(Device.rack_id == rack_id)
            .order_by(
                Device.ru_start.asc().nulls_last(),
                Device.name.asc(),
                Device.id.asc(),
            )
        )
        .scalars()
        .all()
    )

    return [
        DeviceView(
            id=row.id,
            name=row.name,
            role=row.role,
            rack_id=row.rack_id,
            ru_start=row.ru_start,
            ru_size=row.ru_size,
            orientation=row.orientation,
            model=row.model,
            serial=row.serial,
            power_watts=row.power_watts,
        )
        for row in rows
    ]


def cablings_for_project(session: Session, project_id: int) -> list[CablingView]:
    rows = (
        session.execute(
            select(Cabling)
            .where(Cabling.project_id == project_id)
            .order_by(Cabling.normalized_key.asc(), Cabling.id.asc())
        )
        .scalars()
        .all()
    )
    return [
        CablingView(
            id=row.id,
            a_device=row.a_device,
            a_port=row.a_port,
            a_port_type=row.a_port_type,
            b_device=row.b_device,
            b_port=row.b_port,
            b_port_type=row.b_port_type,
            cable_type=row.cable_type,
            label=row.label,
            length=row.length,
            notes=row.notes,
            normalized_key=row.normalized_key,
        )
        for row in rows
    ]


def power_cablings_for_rack(session: Session, rack_id: int) -> list[CablingView]:
    rack = session.get(Rack, rack_id)
    if rack is None:
        return []

    rack_device_names = {
        name
        for (name,) in session.execute(
            select(Device.name).where(
                Device.project_id == rack.project_id, Device.rack_id == rack_id
            )
        ).all()
    }
    if not rack_device_names:
        return []

    rows = (
        session.execute(
            select(PowerCabling)
            .where(
                PowerCabling.project_id == rack.project_id,
                (
                    PowerCabling.a_device.in_(rack_device_names)
                    | PowerCabling.b_device.in_(rack_device_names)
                ),
            )
            .order_by(PowerCabling.normalized_key.asc(), PowerCabling.id.asc())
        )
        .scalars()
        .all()
    )

    return [
        CablingView(
            id=row.id,
            a_device=row.a_device,
            a_port=row.a_port,
            a_port_type=row.a_port_type,
            b_device=row.b_device,
            b_port=row.b_port,
            b_port_type=row.b_port_type,
            cable_type=row.cable_type,
            label=row.label,
            length=row.length,
            notes=row.notes,
            normalized_key=row.normalized_key,
        )
        for row in rows
    ]
