"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from rackwright.models import Base, Cabling, Device, PowerCabling, Project, Rack
from rackwright.view_builders import (
    cablings_for_project,
    devices_in_rack,
    power_cablings_for_rack,
)


def _new_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(engine)


def _seed(session: Session) -> tuple[int, int]:
    project = Project(name="p-vm")
    session.add(project)
    session.flush()

    rack = Rack(project_id=project.id, name="rack-a", rack_height_u=42)
    session.add(rack)
    session.flush()

    session.add_all(
        [
            Device(
                project_id=project.id,
                rack_id=rack.id,
                name="srv2",
                role="Server",
                ru_start=12,
                ru_size=2,
            ),
            Device(
                project_id=project.id,
                rack_id=rack.id,
                name="srv1",
                role="Server",
                ru_start=10,
                ru_size=1,
            ),
            Device(
                project_id=project.id,
                rack_id=rack.id,
                name="pdu-a",
                role="PDU",
                ru_start=None,
                ru_size=None,
            ),
            Device(
                project_id=project.id,
                rack_id=None,
                name="core-sw",
                role="Switch",
                ru_start=None,
                ru_size=None,
            ),
        ]
    )
    session.flush()

    session.add_all(
        [
            Cabling(
                project_id=project.id,
                a_device="srv2",
                a_port="eth1",
                a_port_type="dcim.interface",
                b_device="core-sw",
                b_port="eth10",
                b_port_type="dcim.interface",
                normalized_key="core-sw::eth10::dcim.interface|srv2::eth1::dcim.interface",
            ),
            Cabling(
                project_id=project.id,
                a_device="srv1",
                a_port="eth0",
                a_port_type="dcim.interface",
                b_device="core-sw",
                b_port="eth9",
                b_port_type="dcim.interface",
                normalized_key="core-sw::eth9::dcim.interface|srv1::eth0::dcim.interface",
            ),
        ]
    )

    session.add_all(
        [
            PowerCabling(
                project_id=project.id,
                a_device="srv1",
                a_port="psu-a",
                a_port_type="dcim.powerport",
                b_device="pdu-a",
                b_port="o1",
                b_port_type="dcim.poweroutlet",
                bank="A",
                outlet="1",
                normalized_key="pdu-a::o1::dcim.poweroutlet|srv1::psu-a::dcim.powerport|a|1",
            ),
            PowerCabling(
                project_id=project.id,
                a_device="core-sw",
                a_port="psu-a",
                a_port_type="dcim.powerport",
                b_device="pdu-b",
                b_port="o2",
                b_port_type="dcim.poweroutlet",
                bank="B",
                outlet="2",
                normalized_key="core-sw::psu-a::dcim.powerport|pdu-b::o2::dcim.poweroutlet|b|2",
            ),
        ]
    )

    session.commit()
    return project.id, rack.id


def test_devices_in_rack_content_and_order() -> None:
    with _new_session() as session:
        _, rack_id = _seed(session)
        view = devices_in_rack(session, rack_id)
        assert [row.name for row in view] == ["srv1", "srv2", "pdu-a"]
        assert view[0].ru_start == 10
        assert view[2].ru_start is None


def test_cablings_for_project_is_deterministic() -> None:
    with _new_session() as session:
        project_id, _ = _seed(session)
        first = cablings_for_project(session, project_id)
        second = cablings_for_project(session, project_id)
        assert [r.normalized_key for r in first] == [r.normalized_key for r in second]
        assert [r.normalized_key for r in first] == [
            "core-sw::eth10::dcim.interface|srv2::eth1::dcim.interface",
            "core-sw::eth9::dcim.interface|srv1::eth0::dcim.interface",
        ]


def test_power_cablings_for_rack_filters_to_rack_devices() -> None:
    with _new_session() as session:
        _, rack_id = _seed(session)
        view = power_cablings_for_rack(session, rack_id)
        assert len(view) == 1
        assert view[0].a_device == "srv1"
        assert view[0].b_device == "pdu-a"
