"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import csv
import json
from io import StringIO

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from rackwright.change_logging import register_change_logging_hook
from rackwright.csv_services import (
    apply_cabling_import,
    apply_power_cabling_import,
    dry_run_cabling_import,
    export_cabling_csv,
)
from rackwright.models import Base, Cabling, Device, FieldChangeLog, Project


def _new_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    register_change_logging_hook(Session)
    return Session(engine)


def _setup_project_with_devices(session: Session) -> int:
    project = Project(name="p-csv")
    session.add(project)
    session.flush()
    for name in ["sw1", "sw2", "srv1"]:
        session.add(Device(project_id=project.id, name=name, role="Other"))
    session.commit()
    return project.id


def test_merge_updates_and_does_not_delete_unspecified_rows() -> None:
    with _new_session() as session:
        project_id = _setup_project_with_devices(session)
        session.add(
            Cabling(
                project_id=project_id,
                a_device="sw1",
                a_port="ge-0/0/1",
                a_port_type="dcim.interface",
                b_device="sw2",
                b_port="ge-0/0/1",
                b_port_type="dcim.interface",
                cable_type="cat6",
                label="keep",
                normalized_key="sw1::ge-0/0/1::dcim.interface|sw2::ge-0/0/1::dcim.interface",
            )
        )
        session.add(
            Cabling(
                project_id=project_id,
                a_device="sw1",
                a_port="ge-0/0/2",
                a_port_type="dcim.interface",
                b_device="srv1",
                b_port="eth0",
                b_port_type="dcim.interface",
                cable_type="cat6",
                label="stay",
                normalized_key="srv1::eth0::dcim.interface|sw1::ge-0/0/2::dcim.interface",
            )
        )
        session.commit()

        csv_text = "\n".join(
            [
                "a_device,a_port,a_port_type,b_device,b_port,b_port_type,cable_type,label,length,notes",
                "sw2,ge-0/0/1,dcim.interface,sw1,ge-0/0/1,dcim.interface,cat6a,updated,,",
            ]
        )
        apply_cabling_import(
            session, project_id, csv_text, "network.csv", create_placeholders=False
        )
        session.commit()

        rows = (
            session.query(Cabling)
            .filter(Cabling.project_id == project_id)
            .order_by(Cabling.id)
            .all()
        )
        assert len(rows) == 2
        updated = [
            r
            for r in rows
            if r.normalized_key
            == "sw1::ge-0/0/1::dcim.interface|sw2::ge-0/0/1::dcim.interface"
        ][0]
        assert updated.label == "updated"
        assert updated.cable_type == "cat6a"
        untouched = [
            r
            for r in rows
            if r.normalized_key
            == "srv1::eth0::dcim.interface|sw1::ge-0/0/2::dcim.interface"
        ][0]
        assert untouched.label == "stay"


def test_ab_normalization_prevents_duplicates() -> None:
    with _new_session() as session:
        project_id = _setup_project_with_devices(session)
        csv_text_1 = "\n".join(
            [
                "a_device,a_port,a_port_type,b_device,b_port,b_port_type,cable_type,label,length,notes",
                "sw1,ge-0/0/3,dcim.interface,sw2,ge-0/0/3,dcim.interface,cat6,l1,,",
            ]
        )
        apply_cabling_import(
            session, project_id, csv_text_1, "network.csv", create_placeholders=False
        )
        session.commit()

        csv_text_2 = "\n".join(
            [
                "a_device,a_port,a_port_type,b_device,b_port,b_port_type,cable_type,label,length,notes",
                "sw2,ge-0/0/3,dcim.interface,sw1,ge-0/0/3,dcim.interface,cat6,l2,,",
            ]
        )
        apply_cabling_import(
            session, project_id, csv_text_2, "network.csv", create_placeholders=False
        )
        session.commit()

        rows = session.query(Cabling).filter(Cabling.project_id == project_id).all()
        assert len(rows) == 1
        assert rows[0].label == "l2"


def test_dry_run_unknown_and_placeholder_creation_with_context() -> None:
    with _new_session() as session:
        project_id = _setup_project_with_devices(session)
        csv_text = "\n".join(
            [
                "a_device,a_port,a_port_type,b_device,b_port,b_port_type,cable_type,label,length,notes",
                "sw1,ge-0/0/4,dcim.interface,new-device,eth1,dcim.interface,cat6,new,,",
            ]
        )
        dry_run = dry_run_cabling_import(session, project_id, csv_text)
        assert dry_run["unknown_devices"] == ["new-device"]

        apply_cabling_import(
            session, project_id, csv_text, "import.csv", create_placeholders=True
        )
        session.commit()

        created = (
            session.query(Device)
            .filter(Device.project_id == project_id, Device.name == "new-device")
            .one()
        )
        assert created.role == "Other"

        csv_logs = session.query(FieldChangeLog).order_by(FieldChangeLog.id).all()
        assert len(csv_logs) > 0
        payloads = [json.loads(log.context) for log in csv_logs if log.context]
        assert any(
            payload.get("source") == "csv_import"
            and payload.get("file") == "import.csv"
            for payload in payloads
        )

        exported = export_cabling_csv(session, project_id)
        reader = csv.DictReader(StringIO(exported))
        assert reader.fieldnames is not None
        assert reader.fieldnames[:6] == [
            "a_device",
            "a_port",
            "a_port_type",
            "b_device",
            "b_port",
            "b_port_type",
        ]


def test_power_import_creates_unknown_b_device_as_pdu_role() -> None:
    with _new_session() as session:
        project_id = _setup_project_with_devices(session)
        csv_text = "\n".join(
            [
                "a_device,a_port,a_port_type,b_device,b_port,b_port_type,bank,outlet,cable_type,label,length,notes",
                "srv1,psu-a,dcim.powerport,pdu-new,o1,dcim.poweroutlet,A,1,power,main,,",
            ]
        )

        apply_power_cabling_import(
            session, project_id, csv_text, "power.csv", create_placeholders=True
        )
        session.commit()

        pdu = (
            session.query(Device)
            .filter(Device.project_id == project_id, Device.name == "pdu-new")
            .one()
        )
        assert pdu.role == "PDU"
