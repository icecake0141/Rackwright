"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

import json
from io import BytesIO

from flask import Flask, redirect, render_template, request, send_file, url_for
from sqlalchemy import select
from sqlalchemy.orm import Session

from rackwright.change_logging import register_change_logging_hook
from rackwright.csv_services import (
    apply_cabling_import,
    apply_power_cabling_import,
    dry_run_cabling_import,
    dry_run_power_cabling_import,
    export_cabling_csv,
    export_power_cabling_csv,
)
from rackwright.db import create_sqlite_engine
from rackwright.default_templates import create_zerostage_starter_template_set
from rackwright.diff_service import diff
from rackwright.generation_service import generate
from rackwright.models import (
    ArtifactFile,
    ArtifactVersion,
    Base,
    Cabling,
    Device,
    DiffReport,
    PowerCabling,
    Project,
    Rack,
    Room,
    Row,
    SectionApplicationRule,
    SectionSnapshot,
    Site,
    TemplateSet,
    TemplateSetSnapshot,
)
from rackwright.template_services import (
    create_project_from_template_set,
    create_template_section,
    create_template_set,
    update_template_set,
)


def create_app(database_url: str = "sqlite:///./rackwright.db") -> Flask:
    app = Flask(__name__)
    engine = create_sqlite_engine(database_url)
    Base.metadata.create_all(engine)
    register_change_logging_hook(Session)

    def _latest_version_map(session: Session) -> dict[int, ArtifactVersion]:
        versions = (
            session.execute(
                select(ArtifactVersion).order_by(
                    ArtifactVersion.project_id, ArtifactVersion.version_number.desc()
                )
            )
            .scalars()
            .all()
        )
        result: dict[int, ArtifactVersion] = {}
        for version in versions:
            if version.project_id not in result:
                result[version.project_id] = version
        return result

    @app.route("/")
    def dashboard():
        with Session(engine) as session:
            projects = (
                session.execute(
                    select(Project)
                    .where(Project.is_deleted.is_(False))
                    .order_by(Project.name)
                )
                .scalars()
                .all()
            )
            template_sets = (
                session.execute(select(TemplateSet).order_by(TemplateSet.name))
                .scalars()
                .all()
            )
            latest_versions = _latest_version_map(session)
            return render_template(
                "dashboard.html",
                projects=projects,
                template_sets=template_sets,
                latest_versions=latest_versions,
            )

    @app.route("/projects/new", methods=["POST"])
    def project_new_from_template():
        with Session(engine) as session:
            template_set_id = int(request.form.get("template_set_id", "0"))
            project_name = request.form.get("project_name", "").strip()
            owner = request.form.get("owner", "").strip() or None
            notes = request.form.get("notes", "").strip() or None
            project = create_project_from_template_set(
                session,
                project_name=project_name,
                owner=owner,
                notes=notes,
                template_set_id=template_set_id,
            )
            session.commit()
            return redirect(url_for("project_detail", project_id=project.id))

    @app.route("/projects/<int:project_id>", methods=["GET", "POST"])
    def project_detail(project_id: int):
        with Session(engine) as session:
            project = session.get(Project, project_id)
            if project is None:
                return ("Not Found", 404)

            if request.method == "POST":
                action = request.form.get("action", "save_project")
                if action == "save_project":
                    project.name = request.form.get("name", project.name).strip()
                    project.owner = request.form.get("owner", "").strip() or None
                    project.notes = request.form.get("notes", "").strip() or None
                elif action == "update_site":
                    site_id = int(request.form.get("site_id", "0"))
                    site = session.get(Site, site_id)
                    if site is not None and site.project_id == project_id:
                        site.name = request.form.get("site_name", site.name).strip()
                        site.address = (
                            request.form.get("site_address", "").strip() or None
                        )
                        site.entry_procedure = (
                            request.form.get("site_entry_procedure", "").strip() or None
                        )
                        site.contact_info = (
                            request.form.get("site_contact_info", "").strip() or None
                        )
                elif action == "update_room":
                    room_id = int(request.form.get("room_id", "0"))
                    room = session.get(Room, room_id)
                    if (
                        room is not None
                        and room.site is not None
                        and room.site.project_id == project_id
                    ):
                        room.name = request.form.get("room_name", room.name).strip()
                elif action == "update_row":
                    row_id = int(request.form.get("row_id", "0"))
                    row_obj = session.get(Row, row_id)
                    if (
                        row_obj is not None
                        and row_obj.room is not None
                        and row_obj.room.site is not None
                        and row_obj.room.site.project_id == project_id
                    ):
                        row_obj.name = request.form.get(
                            "row_name", row_obj.name
                        ).strip()
                session.commit()
                return redirect(url_for("project_detail", project_id=project_id))

            racks = (
                session.execute(
                    select(Rack)
                    .where(Rack.project_id == project_id)
                    .order_by(Rack.name)
                )
                .scalars()
                .all()
            )
            devices = (
                session.execute(
                    select(Device)
                    .where(Device.project_id == project_id)
                    .order_by(Device.name)
                )
                .scalars()
                .all()
            )
            sites = (
                session.execute(
                    select(Site)
                    .where(Site.project_id == project_id)
                    .order_by(Site.name)
                )
                .scalars()
                .all()
            )
            rooms = (
                session.execute(
                    select(Room)
                    .join(Site, Site.id == Room.site_id)
                    .where(Site.project_id == project_id)
                    .order_by(Room.name)
                )
                .scalars()
                .all()
            )
            rows = (
                session.execute(
                    select(Row)
                    .join(Room, Room.id == Row.room_id)
                    .join(Site, Site.id == Room.site_id)
                    .where(Site.project_id == project_id)
                    .order_by(Row.name)
                )
                .scalars()
                .all()
            )

            rooms_by_site: dict[int, list[Room]] = {}
            for room in rooms:
                rooms_by_site.setdefault(room.site_id, []).append(room)

            rows_by_room: dict[int, list[Row]] = {}
            for row_obj in rows:
                rows_by_room.setdefault(row_obj.room_id, []).append(row_obj)

            racks_by_row: dict[int, list[Rack]] = {}
            unassigned_racks: list[Rack] = []
            for rack in racks:
                if rack.row_id is None:
                    unassigned_racks.append(rack)
                else:
                    racks_by_row.setdefault(rack.row_id, []).append(rack)

            devices_by_rack: dict[int, list[Device]] = {}
            unassigned_devices: list[Device] = []
            for device in devices:
                if device.rack_id is None:
                    unassigned_devices.append(device)
                else:
                    devices_by_rack.setdefault(device.rack_id, []).append(device)

            hierarchy_tree = []
            for site in sites:
                site_node = {"site": site, "rooms": []}
                for room in rooms_by_site.get(site.id, []):
                    room_node = {"room": room, "rows": []}
                    for row_obj in rows_by_room.get(room.id, []):
                        row_node = {"row": row_obj, "racks": []}
                        for rack in racks_by_row.get(row_obj.id, []):
                            row_node["racks"].append(
                                {
                                    "rack": rack,
                                    "devices": devices_by_rack.get(rack.id, []),
                                }
                            )
                        room_node["rows"].append(row_node)
                    site_node["rooms"].append(room_node)
                hierarchy_tree.append(site_node)

            return render_template(
                "project_detail.html",
                project=project,
                racks=racks,
                devices=devices,
                hierarchy_tree=hierarchy_tree,
                unassigned_racks=unassigned_racks,
                unassigned_devices=unassigned_devices,
            )

    @app.route("/projects/<int:project_id>/section-rules")
    def project_section_rules(project_id: int):
        with Session(engine) as session:
            project = session.get(Project, project_id)
            if project is None:
                return ("Not Found", 404)

            sections = (
                session.execute(
                    select(SectionSnapshot)
                    .join(
                        TemplateSetSnapshot,
                        TemplateSetSnapshot.id
                        == SectionSnapshot.template_set_snapshot_id,
                    )
                    .where(TemplateSetSnapshot.project_id == project_id)
                    .order_by(
                        SectionSnapshot.category,
                        SectionSnapshot.section_order,
                        SectionSnapshot.id,
                    )
                )
                .scalars()
                .all()
            )
            rules = (
                session.execute(
                    select(SectionApplicationRule)
                    .where(SectionApplicationRule.project_id == project_id)
                    .order_by(SectionApplicationRule.section_snapshot_id)
                )
                .scalars()
                .all()
            )
            rules_by_section = {rule.section_snapshot_id: rule for rule in rules}
            rows = []
            for section in sections:
                rule = rules_by_section.get(section.id)
                if rule is None:
                    continue
                rows.append({"section": section, "rule": rule})

            return render_template(
                "project_section_rules.html",
                project=project,
                rows=rows,
            )

    @app.route("/projects/<int:project_id>/section-rules/<int:rule_id>/edit")
    def project_section_rule_edit(project_id: int, rule_id: int):
        with Session(engine) as session:
            project = session.get(Project, project_id)
            if project is None:
                return ("Not Found", 404)

            rule = session.get(SectionApplicationRule, rule_id)
            if rule is None or rule.project_id != project_id:
                return ("Not Found", 404)

            section = session.get(SectionSnapshot, rule.section_snapshot_id)
            if section is None:
                return ("Not Found", 404)

            filters = {}
            if rule.filters_json:
                parsed = json.loads(rule.filters_json)
                if isinstance(parsed, dict):
                    filters = parsed

            role_values = filters.get("role", [])
            rack_scope_values = filters.get("rack_scope", [])

            return render_template(
                "project_section_rules.html",
                project=project,
                rows=[{"section": section, "rule": rule}],
                edit_rule=rule,
                edit_section=section,
                role_values=", ".join([str(x) for x in role_values]),
                rack_scope_values=", ".join([str(x) for x in rack_scope_values]),
            )

    @app.route(
        "/projects/<int:project_id>/section-rules/<int:rule_id>/update",
        methods=["POST"],
    )
    def project_section_rule_update(project_id: int, rule_id: int):
        with Session(engine) as session:
            rule = session.get(SectionApplicationRule, rule_id)
            if rule is None or rule.project_id != project_id:
                return ("Not Found", 404)

            enabled = request.form.get("enabled", "0") == "1"
            role_values = [
                value.strip()
                for value in request.form.get("role_values", "").split(",")
                if value.strip()
            ]
            rack_scope_values = [
                value.strip()
                for value in request.form.get("rack_scope_values", "").split(",")
                if value.strip()
            ]
            filters = {}
            if role_values:
                filters["role"] = role_values
            if rack_scope_values:
                filters["rack_scope"] = rack_scope_values

            rule.enabled = enabled
            rule.filters_json = (
                json.dumps(filters, ensure_ascii=False) if filters else None
            )
            session.commit()
            return redirect(
                url_for(
                    "project_section_rule_edit", project_id=project_id, rule_id=rule_id
                )
            )

    @app.route("/projects/<int:project_id>/racks/new", methods=["POST"])
    def rack_new(project_id: int):
        with Session(engine) as session:
            project = session.get(Project, project_id)
            if project is None:
                return ("Not Found", 404)
            rack = Rack(
                project_id=project_id,
                name=request.form.get("name", "").strip(),
                rack_height_u=int(request.form.get("rack_height_u", "42")),
            )
            session.add(rack)
            session.commit()
            return redirect(url_for("rack_detail", rack_id=rack.id, tab="basics"))

    @app.route("/projects/<int:project_id>/devices/new", methods=["POST"])
    def device_new(project_id: int):
        with Session(engine) as session:
            project = session.get(Project, project_id)
            if project is None:
                return ("Not Found", 404)
            rack_id_raw = request.form.get("rack_id", "")
            device = Device(
                project_id=project_id,
                name=request.form.get("name", "").strip(),
                role=request.form.get("role", "Other").strip() or "Other",
                rack_id=int(rack_id_raw) if rack_id_raw else None,
                ru_start=(
                    int(request.form.get("ru_start", "0"))
                    if request.form.get("ru_start", "").strip()
                    else None
                ),
                ru_size=(
                    int(request.form.get("ru_size", "0"))
                    if request.form.get("ru_size", "").strip()
                    else None
                ),
            )
            session.add(device)
            session.commit()
            return redirect(url_for("device_detail", device_id=device.id, tab="basics"))

    @app.route("/racks/<int:rack_id>", methods=["GET", "POST"])
    def rack_detail(rack_id: int):
        tab = request.args.get("tab", "basics")
        with Session(engine) as session:
            rack = session.get(Rack, rack_id)
            if rack is None:
                return ("Not Found", 404)

            if request.method == "POST":
                action = request.form.get("action", "save_basics")
                if action == "save_basics":
                    rack.name = request.form.get("name", rack.name).strip()
                    rack.rack_height_u = int(
                        request.form.get("rack_height_u", str(rack.rack_height_u))
                    )
                elif action == "save_layout":
                    for device in rack.devices:
                        ru_start_val = request.form.get(
                            f"ru_start_{device.id}", ""
                        ).strip()
                        ru_size_val = request.form.get(
                            f"ru_size_{device.id}", ""
                        ).strip()
                        orientation_val = request.form.get(
                            f"orientation_{device.id}", ""
                        ).strip()
                        device.ru_start = int(ru_start_val) if ru_start_val else None
                        device.ru_size = int(ru_size_val) if ru_size_val else None
                        device.orientation = orientation_val or None
                session.commit()
                return redirect(url_for("rack_detail", rack_id=rack_id, tab=tab))

            devices = (
                session.execute(
                    select(Device)
                    .where(Device.rack_id == rack_id)
                    .order_by(Device.name)
                )
                .scalars()
                .all()
            )
            power_rows = (
                session.execute(
                    select(PowerCabling)
                    .where(PowerCabling.project_id == rack.project_id)
                    .order_by(PowerCabling.normalized_key)
                )
                .scalars()
                .all()
            )
            return render_template(
                "rack_detail.html",
                rack=rack,
                devices=devices,
                power_rows=power_rows,
                tab=tab,
            )

    @app.route("/devices/<int:device_id>", methods=["GET", "POST"])
    def device_detail(device_id: int):
        tab = request.args.get("tab", "basics")
        with Session(engine) as session:
            device = session.get(Device, device_id)
            if device is None:
                return ("Not Found", 404)

            if request.method == "POST":
                action = request.form.get("action", "save_basics")
                if action == "save_basics":
                    device.name = request.form.get("name", device.name).strip()
                    device.role = request.form.get("role", device.role).strip()
                    device.model = request.form.get("model", "").strip() or None
                    device.serial = request.form.get("serial", "").strip() or None
                elif action == "save_settings":
                    device.device_vars = (
                        request.form.get("device_vars", "").strip() or None
                    )
                elif action == "save_power":
                    watts = request.form.get("power_watts", "").strip()
                    device.power_watts = int(watts) if watts else None
                session.commit()
                return redirect(url_for("device_detail", device_id=device_id, tab=tab))

            cablings = (
                session.execute(
                    select(Cabling)
                    .where(
                        (Cabling.a_device == device.name)
                        | (Cabling.b_device == device.name),
                        Cabling.project_id == device.project_id,
                    )
                    .order_by(Cabling.normalized_key)
                )
                .scalars()
                .all()
            )
            power_rows = (
                session.execute(
                    select(PowerCabling)
                    .where(
                        (PowerCabling.a_device == device.name)
                        | (PowerCabling.b_device == device.name),
                        PowerCabling.project_id == device.project_id,
                    )
                    .order_by(PowerCabling.normalized_key)
                )
                .scalars()
                .all()
            )
            return render_template(
                "device_detail.html",
                device=device,
                cablings=cablings,
                power_rows=power_rows,
                tab=tab,
            )

    @app.route("/projects/<int:project_id>/cabling", methods=["GET", "POST"])
    def project_cabling(project_id: int):
        with Session(engine) as session:
            project = session.get(Project, project_id)
            if project is None:
                return ("Not Found", 404)

            message = None
            dry_run_unknown: list[str] = []

            if request.method == "POST":
                action = request.form.get("action", "save_row")
                if action == "save_row":
                    row_id = int(request.form.get("row_id", "0"))
                    row = session.get(Cabling, row_id)
                    if row is not None and row.project_id == project_id:
                        row.label = request.form.get("label", "").strip() or None
                        row.cable_type = (
                            request.form.get("cable_type", "").strip() or None
                        )
                        row.notes = request.form.get("notes", "").strip() or None
                        session.commit()
                elif action == "import_csv":
                    csv_type = request.form.get("csv_type", "network")
                    csv_text = request.form.get("csv_text", "")
                    file_name = request.form.get("file_name", "upload.csv")
                    confirm = (
                        request.form.get("confirm_create_placeholders", "0") == "1"
                    )
                    if csv_type == "network":
                        dry = dry_run_cabling_import(session, project_id, csv_text)
                        dry_run_unknown = list(dry["unknown_devices"])
                        if dry_run_unknown and not confirm:
                            message = "Unknown devices found. Confirm placeholder creation to apply."
                        else:
                            apply_cabling_import(
                                session,
                                project_id,
                                csv_text,
                                file_name,
                                create_placeholders=confirm,
                            )
                            session.commit()
                            message = "Network CSV import applied."
                    else:
                        dry = dry_run_power_cabling_import(
                            session, project_id, csv_text
                        )
                        dry_run_unknown = list(dry["unknown_devices"])
                        if dry_run_unknown and not confirm:
                            message = "Unknown devices found. Confirm placeholder creation to apply."
                        else:
                            apply_power_cabling_import(
                                session,
                                project_id,
                                csv_text,
                                file_name,
                                create_placeholders=confirm,
                            )
                            session.commit()
                            message = "Power CSV import applied."

            filter_device = request.args.get("device", "").strip()
            filter_rack = request.args.get("rack", "").strip()
            filter_row = request.args.get("row", "").strip()

            racks = (
                session.execute(
                    select(Rack)
                    .where(Rack.project_id == project_id)
                    .order_by(Rack.name)
                )
                .scalars()
                .all()
            )
            row_ids_in_project = {
                rack.row_id for rack in racks if rack.row_id is not None
            }
            rows_in_project = (
                session.execute(
                    select(Row).where(Row.id.in_(row_ids_in_project)).order_by(Row.name)
                )
                .scalars()
                .all()
                if row_ids_in_project
                else []
            )
            device_options = [
                device.name
                for device in session.execute(
                    select(Device)
                    .where(Device.project_id == project_id)
                    .order_by(Device.name)
                )
                .scalars()
                .all()
            ]

            scoped_device_names: set[str] | None = None
            if filter_rack:
                rack_devices = {
                    name
                    for (name,) in session.execute(
                        select(Device.name).where(
                            Device.project_id == project_id,
                            Device.rack_id == int(filter_rack),
                        )
                    ).all()
                }
                scoped_device_names = (
                    rack_devices
                    if scoped_device_names is None
                    else scoped_device_names & rack_devices
                )

            if filter_row:
                row_rack_ids = {
                    rack_id
                    for (rack_id,) in session.execute(
                        select(Rack.id).where(
                            Rack.project_id == project_id,
                            Rack.row_id == int(filter_row),
                        )
                    ).all()
                }
                row_devices = {
                    name
                    for (name,) in session.execute(
                        select(Device.name).where(
                            Device.project_id == project_id,
                            Device.rack_id.in_(row_rack_ids),
                        )
                    ).all()
                }
                scoped_device_names = (
                    row_devices
                    if scoped_device_names is None
                    else scoped_device_names & row_devices
                )

            if filter_device:
                device_set = {filter_device}
                scoped_device_names = (
                    device_set
                    if scoped_device_names is None
                    else scoped_device_names & device_set
                )

            rows_query = select(Cabling).where(Cabling.project_id == project_id)
            power_query = select(PowerCabling).where(
                PowerCabling.project_id == project_id
            )
            if scoped_device_names is not None:
                if scoped_device_names:
                    rows_query = rows_query.where(
                        (Cabling.a_device.in_(scoped_device_names))
                        | (Cabling.b_device.in_(scoped_device_names))
                    )
                    power_query = power_query.where(
                        (PowerCabling.a_device.in_(scoped_device_names))
                        | (PowerCabling.b_device.in_(scoped_device_names))
                    )
                else:
                    rows_query = rows_query.where(Cabling.id == -1)
                    power_query = power_query.where(PowerCabling.id == -1)

            rows = (
                session.execute(rows_query.order_by(Cabling.normalized_key))
                .scalars()
                .all()
            )
            power_rows = (
                session.execute(power_query.order_by(PowerCabling.normalized_key))
                .scalars()
                .all()
            )
            return render_template(
                "project_cabling.html",
                project=project,
                rows=rows,
                power_rows=power_rows,
                message=message,
                dry_run_unknown=dry_run_unknown,
                filter_device=filter_device,
                filter_rack=filter_rack,
                filter_row=filter_row,
                rack_options=racks,
                row_options=rows_in_project,
                device_options=device_options,
            )

    @app.route("/projects/<int:project_id>/cabling/export/<string:csv_type>")
    def export_cabling(project_id: int, csv_type: str):
        with Session(engine) as session:
            if csv_type == "network":
                content = export_cabling_csv(session, project_id)
                filename = "network_cabling.csv"
            elif csv_type == "power":
                content = export_power_cabling_csv(session, project_id)
                filename = "power_cabling.csv"
            else:
                return ("Not Found", 404)
            tmp_path = BytesIO(content.encode("utf-8"))
            return send_file(
                tmp_path,
                as_attachment=True,
                download_name=filename,
                mimetype="text/csv",
            )

    @app.route("/projects/<int:project_id>/generate", methods=["GET", "POST"])
    def project_generate(project_id: int):
        with Session(engine) as session:
            project = session.get(Project, project_id)
            if project is None:
                return ("Not Found", 404)

            message = None
            if request.method == "POST":
                mode = request.form.get("mode", "all")
                remarks = request.form.get("remarks", "").strip() or None
                base_raw = request.form.get("base_version_id", "").strip()
                base_version_id = int(base_raw) if base_raw else None
                conflict_action = request.form.get("conflict_action", "stop")
                result = generate(session, project_id, mode, base_version_id, remarks)
                if result.skipped:
                    if conflict_action == "stop":
                        message = f"Skipped (existing version {result.artifact_version.version_number})."
                    elif conflict_action == "force":
                        forced = generate(
                            session,
                            project_id,
                            mode,
                            base_version_id,
                            remarks,
                            force=True,
                        )
                        message = f"Forced generation created version {forced.artifact_version.version_number}."
                    elif conflict_action == "save-and-regenerate":
                        project.revision += 1
                        session.flush()
                        retry = generate(
                            session, project_id, mode, base_version_id, remarks
                        )
                        if retry.skipped:
                            message = f"Saved revision, but existing version {retry.artifact_version.version_number} still matched."
                        else:
                            message = f"Saved and regenerated version {retry.artifact_version.version_number}."
                    else:
                        message = f"Skipped (existing version {result.artifact_version.version_number})."
                else:
                    message = (
                        f"Generated version {result.artifact_version.version_number}."
                    )
                session.commit()

            versions = (
                session.execute(
                    select(ArtifactVersion)
                    .where(ArtifactVersion.project_id == project_id)
                    .order_by(ArtifactVersion.version_number.desc())
                )
                .scalars()
                .all()
            )
            return render_template(
                "project_generate.html",
                project=project,
                versions=versions,
                message=message,
            )

    @app.route("/projects/<int:project_id>/versions")
    def project_versions(project_id: int):
        with Session(engine) as session:
            project = session.get(Project, project_id)
            if project is None:
                return ("Not Found", 404)
            versions = (
                session.execute(
                    select(ArtifactVersion)
                    .where(ArtifactVersion.project_id == project_id)
                    .order_by(ArtifactVersion.version_number.desc())
                )
                .scalars()
                .all()
            )
            diff_reports = (
                session.execute(
                    select(DiffReport)
                    .where(DiffReport.project_id == project_id)
                    .order_by(DiffReport.id.desc())
                )
                .scalars()
                .all()
            )
            return render_template(
                "project_versions.html",
                project=project,
                versions=versions,
                diff_reports=diff_reports,
            )

    @app.route("/projects/<int:project_id>/versions/compare", methods=["POST"])
    def versions_compare(project_id: int):
        with Session(engine) as session:
            from_version_id = int(request.form.get("from_version_id", "0"))
            to_version_id = int(request.form.get("to_version_id", "0"))
            diff(session, from_version_id, to_version_id)
            session.commit()
            return redirect(url_for("project_versions", project_id=project_id))

    @app.route("/artifacts/<int:artifact_file_id>/download")
    def download_artifact(artifact_file_id: int):
        with Session(engine) as session:
            artifact = session.get(ArtifactFile, artifact_file_id)
            if artifact is None:
                return ("Not Found", 404)
            from rackwright.generation_service import _data_dir as generation_data_dir

            real_base = generation_data_dir()
            file_path = real_base / artifact.relative_path
            if not file_path.exists():
                return ("Not Found", 404)
            return send_file(
                file_path, as_attachment=True, download_name=file_path.name
            )

    @app.route("/projects/<int:project_id>/errors")
    def project_errors(project_id: int):
        with Session(engine) as session:
            project = session.get(Project, project_id)
            if project is None:
                return ("Not Found", 404)

            versions = (
                session.execute(
                    select(ArtifactVersion)
                    .where(ArtifactVersion.project_id == project_id)
                    .order_by(ArtifactVersion.version_number.desc())
                )
                .scalars()
                .all()
            )
            version_errors: list[tuple[ArtifactVersion, list[dict[str, object]]]] = []
            for version in versions:
                payload = json.loads(version.errors_json) if version.errors_json else []
                if payload:
                    version_errors.append((version, payload))

            return render_template(
                "project_errors.html", project=project, version_errors=version_errors
            )

    @app.route("/projects/<int:project_id>/errors/jump")
    def errors_jump(project_id: int):
        kind = request.args.get("kind", "")
        value = request.args.get("value", "")
        if kind == "section":
            return redirect(
                url_for("project_generate", project_id=project_id) + f"#section-{value}"
            )
        if kind == "csv_row":
            return redirect(
                url_for("project_cabling", project_id=project_id, row=value)
            )
        return redirect(url_for("project_errors", project_id=project_id))

    @app.route("/template-sets")
    def template_sets_list():
        with Session(engine) as session:
            template_sets = (
                session.execute(select(TemplateSet).order_by(TemplateSet.name))
                .scalars()
                .all()
            )
            return render_template(
                "template_sets_list.html", template_sets=template_sets
            )

    @app.route("/template-sets/new", methods=["GET", "POST"])
    def template_set_new():
        if request.method == "POST":
            with Session(engine) as session:
                create_template_set(
                    session,
                    name=request.form.get("name", "").strip(),
                    description=request.form.get("description", "").strip() or None,
                )
                session.commit()
            return redirect(url_for("template_sets_list"))
        return render_template("template_set_form.html", template_set=None, sections=[])

    @app.route("/template-sets/bootstrap/zerostage", methods=["POST"])
    def template_set_bootstrap_zerostage():
        with Session(engine) as session:
            template_set = create_zerostage_starter_template_set(session)
            session.commit()
            return redirect(
                url_for("template_set_edit", template_set_id=template_set.id)
            )

    @app.route("/template-sets/<int:template_set_id>/edit", methods=["GET", "POST"])
    def template_set_edit(template_set_id: int):
        with Session(engine) as session:
            template_set = session.get(TemplateSet, template_set_id)
            if template_set is None:
                return ("Not Found", 404)

            if request.method == "POST":
                update_template_set(
                    session,
                    template_set_id,
                    name=request.form.get("name", "").strip(),
                    description=request.form.get("description", "").strip() or None,
                )
                session.commit()
                return redirect(
                    url_for("template_set_edit", template_set_id=template_set_id)
                )

            sections = sorted(
                template_set.sections, key=lambda s: (s.category, s.section_order)
            )
            return render_template(
                "template_set_form.html", template_set=template_set, sections=sections
            )

    @app.route("/template-sets/<int:template_set_id>/sections/new", methods=["POST"])
    def template_section_new(template_set_id: int):
        with Session(engine) as session:
            template_set = session.get(TemplateSet, template_set_id)
            if template_set is None:
                return ("Not Found", 404)

            output_targets_raw = request.form.get("output_targets", "[]")
            applicable_roles_raw = request.form.get("applicable_roles", "")

            create_template_section(
                session,
                template_set_id,
                target_type=request.form.get("target_type", "Project").strip(),
                category=request.form.get("category", "General").strip(),
                section_order=int(request.form.get("section_order", "1")),
                output_targets=json.loads(output_targets_raw),
                applicable_roles=(
                    json.loads(applicable_roles_raw) if applicable_roles_raw else None
                ),
                text=request.form.get("text", "").strip(),
            )
            session.commit()
        return redirect(url_for("template_set_edit", template_set_id=template_set_id))

    return app
