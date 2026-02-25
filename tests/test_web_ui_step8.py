"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from rackwright.app import create_app
from rackwright.models import (
    ArtifactVersion,
    Base,
    Cabling,
    Device,
    Project,
    Rack,
    Room,
    Row,
    SectionApplicationRule,
    Site,
    TemplateSet,
)
from rackwright.template_services import create_template_section, create_template_set


@pytest.fixture()
def client(tmp_path: Path):
    db_path = tmp_path / "ui.db"
    os.environ["RACKWRIGHT_DATA_DIR"] = str(tmp_path / "data")
    app = create_app(f"sqlite:///{db_path}")
    app.testing = True
    with app.test_client() as c:
        yield c


def _seed_template(db_url: str) -> tuple[int, int]:
    engine = create_engine(db_url, future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        ts = create_template_set(session, "ui-ts", "desc")
        create_template_section(
            session,
            ts.id,
            target_type="Project",
            category="General",
            section_order=1,
            output_targets=["word", "excel"],
            applicable_roles=None,
            text="hello {{ project.name }}",
        )
        session.commit()
        return ts.id, session.query(TemplateSet).count()


def test_core_ui_flows(client, tmp_path: Path) -> None:
    db_url = f"sqlite:///{tmp_path / 'ui.db'}"
    template_set_id, _ = _seed_template(db_url)

    res = client.get("/")
    assert res.status_code == 200

    res = client.post(
        "/projects/new",
        data={
            "project_name": "ui-project",
            "owner": "owner",
            "notes": "n",
            "template_set_id": str(template_set_id),
        },
        follow_redirects=False,
    )
    assert res.status_code in (302, 303)
    location = res.headers["Location"]
    assert "/projects/" in location

    project_path = location
    res = client.get(project_path)
    assert res.status_code == 200

    project_id = int(project_path.rstrip("/").split("/")[-1])
    res = client.post(
        f"/projects/{project_id}/racks/new",
        data={"name": "rack-1", "rack_height_u": "42"},
        follow_redirects=False,
    )
    assert res.status_code in (302, 303)
    rack_path = res.headers["Location"]
    res = client.get(rack_path)
    assert res.status_code == 200

    res = client.post(
        f"/projects/{project_id}/devices/new",
        data={
            "name": "dev-1",
            "role": "Server",
            "rack_id": "",
            "ru_start": "",
            "ru_size": "",
        },
        follow_redirects=False,
    )
    assert res.status_code in (302, 303)
    device_path = res.headers["Location"]
    assert client.get(device_path).status_code == 200

    csv_text = (
        "a_device,a_port,a_port_type,b_device,b_port,b_port_type,cable_type,label,length,notes\n"
        "dev-1,eth0,dcim.interface,new-sw,eth1,dcim.interface,cat6,l1,,"
    )
    res = client.post(
        f"/projects/{project_id}/cabling",
        data={
            "action": "import_csv",
            "csv_type": "network",
            "file_name": "import.csv",
            "csv_text": csv_text,
            "confirm_create_placeholders": "1",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200

    assert (
        client.get(f"/projects/{project_id}/cabling/export/network").status_code == 200
    )

    res = client.post(
        f"/projects/{project_id}/generate",
        data={
            "mode": "all",
            "remarks": "run",
            "base_version_id": "",
            "conflict_action": "stop",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200

    res = client.get(f"/projects/{project_id}/versions")
    assert res.status_code == 200

    with Session(create_engine(db_url, future=True)) as session:
        versions = (
            session.query(Project)
            .filter(Project.id == project_id)
            .one()
            .artifact_versions
        )
        assert len(versions) >= 1
        if len(versions) == 1:
            client.post(
                f"/projects/{project_id}/generate",
                data={
                    "mode": "all",
                    "remarks": "run2",
                    "base_version_id": "",
                    "conflict_action": "force",
                },
                follow_redirects=True,
            )

    with Session(create_engine(db_url, future=True)) as session:
        p = session.query(Project).filter(Project.id == project_id).one()
        versions = sorted(p.artifact_versions, key=lambda v: v.version_number)
        if len(versions) >= 2:
            res = client.post(
                f"/projects/{project_id}/versions/compare",
                data={
                    "from_version_id": str(versions[0].id),
                    "to_version_id": str(versions[-1].id),
                },
                follow_redirects=False,
            )
            assert res.status_code in (302, 303)

    assert client.get(f"/projects/{project_id}/errors").status_code == 200
    assert client.get(
        f"/projects/{project_id}/errors/jump?kind=section&value=excel-render",
        follow_redirects=False,
    ).status_code in (302, 303)
    assert client.get(
        f"/projects/{project_id}/errors/jump?kind=csv_row&value=2",
        follow_redirects=False,
    ).status_code in (302, 303)


def test_cabling_filters_support_rack_row_device(client, tmp_path: Path) -> None:
    db_url = f"sqlite:///{tmp_path / 'ui.db'}"
    template_set_id, _ = _seed_template(db_url)

    res = client.post(
        "/projects/new",
        data={
            "project_name": "filter-ui-project",
            "owner": "owner",
            "notes": "n",
            "template_set_id": str(template_set_id),
        },
        follow_redirects=False,
    )
    assert res.status_code in (302, 303)
    project_id = int(res.headers["Location"].rstrip("/").split("/")[-1])

    engine = create_engine(db_url, future=True)
    with Session(engine) as session:
        site = Site(project_id=project_id, name="site-a")
        session.add(site)
        session.flush()
        room = Room(site_id=site.id, name="room-a")
        session.add(room)
        session.flush()
        row_a = Row(room_id=room.id, name="row-a")
        row_b = Row(room_id=room.id, name="row-b")
        session.add_all([row_a, row_b])
        session.flush()

        rack_a = Rack(
            project_id=project_id, row_id=row_a.id, name="rack-a", rack_height_u=42
        )
        rack_b = Rack(
            project_id=project_id, row_id=row_b.id, name="rack-b", rack_height_u=42
        )
        session.add_all([rack_a, rack_b])
        session.flush()

        session.add_all(
            [
                Device(
                    project_id=project_id,
                    rack_id=rack_a.id,
                    name="dev-a",
                    role="Server",
                ),
                Device(
                    project_id=project_id,
                    rack_id=rack_b.id,
                    name="dev-b",
                    role="Server",
                ),
                Device(project_id=project_id, rack_id=None, name="core", role="Switch"),
            ]
        )
        session.flush()

        session.add_all(
            [
                Cabling(
                    project_id=project_id,
                    a_device="dev-a",
                    a_port="eth0",
                    a_port_type="dcim.interface",
                    b_device="core",
                    b_port="eth1",
                    b_port_type="dcim.interface",
                    label="rack-a-link",
                    normalized_key="core::eth1::dcim.interface|dev-a::eth0::dcim.interface",
                ),
                Cabling(
                    project_id=project_id,
                    a_device="dev-b",
                    a_port="eth0",
                    a_port_type="dcim.interface",
                    b_device="core",
                    b_port="eth2",
                    b_port_type="dcim.interface",
                    label="rack-b-link",
                    normalized_key="core::eth2::dcim.interface|dev-b::eth0::dcim.interface",
                ),
            ]
        )
        session.commit()
        rack_a_id = rack_a.id
        row_a_id = row_a.id

    rack_filtered = client.get(f"/projects/{project_id}/cabling?rack={rack_a_id}")
    assert rack_filtered.status_code == 200
    assert b"rack-a-link" in rack_filtered.data
    assert b"rack-b-link" not in rack_filtered.data

    row_filtered = client.get(f"/projects/{project_id}/cabling?row={row_a_id}")
    assert row_filtered.status_code == 200
    assert b"rack-a-link" in row_filtered.data
    assert b"rack-b-link" not in row_filtered.data

    device_filtered = client.get(f"/projects/{project_id}/cabling?device=dev-b")
    assert device_filtered.status_code == 200
    assert b"rack-a-link" not in device_filtered.data
    assert b"rack-b-link" in device_filtered.data


def test_project_detail_shows_hierarchy_tree(client, tmp_path: Path) -> None:
    db_url = f"sqlite:///{tmp_path / 'ui.db'}"
    template_set_id, _ = _seed_template(db_url)

    res = client.post(
        "/projects/new",
        data={
            "project_name": "tree-project",
            "owner": "owner",
            "notes": "n",
            "template_set_id": str(template_set_id),
        },
        follow_redirects=False,
    )
    assert res.status_code in (302, 303)
    project_id = int(res.headers["Location"].rstrip("/").split("/")[-1])

    engine = create_engine(db_url, future=True)
    with Session(engine) as session:
        site = Site(project_id=project_id, name="site-t")
        session.add(site)
        session.flush()
        room = Room(site_id=site.id, name="room-t")
        session.add(room)
        session.flush()
        row = Row(room_id=room.id, name="row-t")
        session.add(row)
        session.flush()
        rack = Rack(
            project_id=project_id, row_id=row.id, name="rack-t", rack_height_u=42
        )
        session.add(rack)
        session.flush()
        session.add(
            Device(project_id=project_id, rack_id=rack.id, name="dev-t", role="Server")
        )
        session.commit()

    page = client.get(f"/projects/{project_id}")
    assert page.status_code == 200
    assert b"Hierarchy Tree" in page.data
    assert b"Site: site-t" in page.data
    assert b"Room: room-t" in page.data
    assert b"Row: row-t" in page.data
    assert b"rack-t" in page.data
    assert b"dev-t" in page.data


def test_generation_conflict_actions_have_distinct_behaviors(
    client, tmp_path: Path
) -> None:
    db_url = f"sqlite:///{tmp_path / 'ui.db'}"
    template_set_id, _ = _seed_template(db_url)

    res = client.post(
        "/projects/new",
        data={
            "project_name": "conflict-project",
            "owner": "owner",
            "notes": "n",
            "template_set_id": str(template_set_id),
        },
        follow_redirects=False,
    )
    assert res.status_code in (302, 303)
    project_id = int(res.headers["Location"].rstrip("/").split("/")[-1])

    # initial generation
    r = client.post(
        f"/projects/{project_id}/generate",
        data={
            "mode": "all",
            "remarks": "run",
            "base_version_id": "",
            "conflict_action": "stop",
        },
        follow_redirects=True,
    )
    assert r.status_code == 200

    engine = create_engine(db_url, future=True)
    with Session(engine) as session:
        project = session.query(Project).filter(Project.id == project_id).one()
        initial_revision = project.revision
        initial_count = (
            session.query(ArtifactVersion)
            .filter(ArtifactVersion.project_id == project_id)
            .count()
        )

    # stop -> no new version
    client.post(
        f"/projects/{project_id}/generate",
        data={
            "mode": "all",
            "remarks": "run",
            "base_version_id": "",
            "conflict_action": "stop",
        },
        follow_redirects=True,
    )
    with Session(engine) as session:
        count_after_stop = (
            session.query(ArtifactVersion)
            .filter(ArtifactVersion.project_id == project_id)
            .count()
        )
        revision_after_stop = (
            session.query(Project).filter(Project.id == project_id).one().revision
        )
    assert count_after_stop == initial_count
    assert revision_after_stop == initial_revision

    # force -> new version without revision bump
    client.post(
        f"/projects/{project_id}/generate",
        data={
            "mode": "all",
            "remarks": "run",
            "base_version_id": "",
            "conflict_action": "force",
        },
        follow_redirects=True,
    )
    with Session(engine) as session:
        count_after_force = (
            session.query(ArtifactVersion)
            .filter(ArtifactVersion.project_id == project_id)
            .count()
        )
        revision_after_force = (
            session.query(Project).filter(Project.id == project_id).one().revision
        )
    assert count_after_force == initial_count + 1
    assert revision_after_force == initial_revision

    # save-and-regenerate -> revision bump and new version
    client.post(
        f"/projects/{project_id}/generate",
        data={
            "mode": "all",
            "remarks": "run",
            "base_version_id": "",
            "conflict_action": "save-and-regenerate",
        },
        follow_redirects=True,
    )
    with Session(engine) as session:
        count_after_save = (
            session.query(ArtifactVersion)
            .filter(ArtifactVersion.project_id == project_id)
            .count()
        )
        revision_after_save = (
            session.query(Project).filter(Project.id == project_id).one().revision
        )
    assert count_after_save == initial_count + 2
    assert revision_after_save == initial_revision + 1


def test_section_rule_routes_support_get_and_post_update(
    client, tmp_path: Path
) -> None:
    db_url = f"sqlite:///{tmp_path / 'ui.db'}"
    template_set_id, _ = _seed_template(db_url)

    res = client.post(
        "/projects/new",
        data={
            "project_name": "rules-project",
            "owner": "owner",
            "notes": "n",
            "template_set_id": str(template_set_id),
        },
        follow_redirects=False,
    )
    assert res.status_code in (302, 303)
    project_id = int(res.headers["Location"].rstrip("/").split("/")[-1])

    rules_page = client.get(f"/projects/{project_id}/section-rules")
    assert rules_page.status_code == 200
    assert b"Section Rules" in rules_page.data

    engine = create_engine(db_url, future=True)
    with Session(engine) as session:
        rule = (
            session.query(SectionApplicationRule)
            .filter(SectionApplicationRule.project_id == project_id)
            .first()
        )
        assert rule is not None
        rule_id = rule.id

    edit_page = client.get(f"/projects/{project_id}/section-rules/{rule_id}/edit")
    assert edit_page.status_code == 200
    assert b"Edit Rule" in edit_page.data

    update_res = client.post(
        f"/projects/{project_id}/section-rules/{rule_id}/update",
        data={
            "role_values": "Server, Switch",
            "rack_scope_values": "rack-a, 1",
        },
        follow_redirects=False,
    )
    assert update_res.status_code in (302, 303)

    with Session(engine) as session:
        updated = session.get(SectionApplicationRule, rule_id)
        assert updated is not None
        assert updated.enabled is False
        assert updated.filters_json is not None
        assert "Server" in updated.filters_json
        assert "rack-a" in updated.filters_json


def test_project_detail_can_edit_site_room_row(client, tmp_path: Path) -> None:
    db_url = f"sqlite:///{tmp_path / 'ui.db'}"
    template_set_id, _ = _seed_template(db_url)

    res = client.post(
        "/projects/new",
        data={
            "project_name": "hier-edit-project",
            "owner": "owner",
            "notes": "n",
            "template_set_id": str(template_set_id),
        },
        follow_redirects=False,
    )
    assert res.status_code in (302, 303)
    project_id = int(res.headers["Location"].rstrip("/").split("/")[-1])

    engine = create_engine(db_url, future=True)
    with Session(engine) as session:
        site = Site(project_id=project_id, name="site-old")
        session.add(site)
        session.flush()
        room = Room(site_id=site.id, name="room-old")
        session.add(room)
        session.flush()
        row = Row(room_id=room.id, name="row-old")
        session.add(row)
        session.commit()
        site_id = site.id
        room_id = room.id
        row_id = row.id

    page = client.get(f"/projects/{project_id}")
    assert page.status_code == 200
    assert b"Edit Site" in page.data
    assert b"Edit Room" in page.data
    assert b"Edit Row" in page.data

    client.post(
        f"/projects/{project_id}",
        data={
            "action": "update_site",
            "site_id": str(site_id),
            "site_name": "site-new",
            "site_address": "addr",
            "site_entry_procedure": "entry",
            "site_contact_info": "contact",
        },
        follow_redirects=False,
    )
    client.post(
        f"/projects/{project_id}",
        data={
            "action": "update_room",
            "room_id": str(room_id),
            "room_name": "room-new",
        },
        follow_redirects=False,
    )
    client.post(
        f"/projects/{project_id}",
        data={
            "action": "update_row",
            "row_id": str(row_id),
            "row_name": "row-new",
        },
        follow_redirects=False,
    )

    with Session(engine) as session:
        updated_site = session.get(Site, site_id)
        updated_room = session.get(Room, room_id)
        updated_row = session.get(Row, row_id)
        assert updated_site is not None
        assert updated_room is not None
        assert updated_row is not None
        assert updated_site.name == "site-new"
        assert updated_site.address == "addr"
        assert updated_room.name == "room-new"
        assert updated_row.name == "row-new"
