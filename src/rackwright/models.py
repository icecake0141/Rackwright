"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class Project(TimestampMixin, Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    owner: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    revision: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    sites: Mapped[list[Site]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    racks: Mapped[list[Rack]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    devices: Mapped[list[Device]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    cablings: Mapped[list[Cabling]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    power_cablings: Mapped[list[PowerCabling]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    template_snapshots: Mapped[list[TemplateSetSnapshot]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    section_application_rules: Mapped[list[SectionApplicationRule]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    artifact_versions: Mapped[list[ArtifactVersion]] = relationship(
        back_populates="project"
    )
    diff_reports: Mapped[list[DiffReport]] = relationship(back_populates="project")
    field_change_logs: Mapped[list[FieldChangeLog]] = relationship(
        back_populates="project"
    )


class Site(TimestampMixin, Base):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    entry_procedure: Mapped[str | None] = mapped_column(Text)
    contact_info: Mapped[str | None] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="sites")
    rooms: Mapped[list[Room]] = relationship(
        back_populates="site", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_sites_project_name"),
    )


class Room(TimestampMixin, Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(
        ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    site: Mapped[Site] = relationship(back_populates="rooms")
    rows: Mapped[list[Row]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("site_id", "name", name="uq_rooms_site_name"),)


class Row(TimestampMixin, Base):
    __tablename__ = "rows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    room: Mapped[Room] = relationship(back_populates="rows")
    racks: Mapped[list[Rack]] = relationship(
        back_populates="row", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("room_id", "name", name="uq_rows_room_name"),)


class Rack(TimestampMixin, Base):
    __tablename__ = "racks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    row_id: Mapped[int | None] = mapped_column(
        ForeignKey("rows.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rack_height_u: Mapped[int] = mapped_column(Integer, nullable=False, default=42)

    project: Mapped[Project] = relationship(back_populates="racks")
    row: Mapped[Row | None] = relationship(back_populates="racks")
    devices: Mapped[list[Device]] = relationship(
        back_populates="rack", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_racks_project_name"),
        Index("ix_racks_project_row", "project_id", "row_id"),
    )


class Device(TimestampMixin, Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rack_id: Mapped[int | None] = mapped_column(
        ForeignKey("racks.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False, default="Other")
    model: Mapped[str | None] = mapped_column(String(255))
    serial: Mapped[str | None] = mapped_column(String(255))
    power_watts: Mapped[int | None] = mapped_column(Integer)
    ru_start: Mapped[int | None] = mapped_column(Integer)
    ru_size: Mapped[int | None] = mapped_column(Integer)
    orientation: Mapped[str | None] = mapped_column(String(32))
    device_vars: Mapped[str | None] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="devices")
    rack: Mapped[Rack | None] = relationship(back_populates="devices")

    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_devices_project_name"),
        Index("ix_devices_project_rack", "project_id", "rack_id"),
    )


class Cabling(TimestampMixin, Base):
    __tablename__ = "cablings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    a_device: Mapped[str] = mapped_column(String(255), nullable=False)
    a_port: Mapped[str] = mapped_column(String(255), nullable=False)
    a_port_type: Mapped[str] = mapped_column(String(64), nullable=False)
    b_device: Mapped[str] = mapped_column(String(255), nullable=False)
    b_port: Mapped[str] = mapped_column(String(255), nullable=False)
    b_port_type: Mapped[str] = mapped_column(String(64), nullable=False)
    cable_type: Mapped[str | None] = mapped_column(String(64))
    label: Mapped[str | None] = mapped_column(String(255))
    length: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)
    normalized_key: Mapped[str] = mapped_column(String(1024), nullable=False)

    project: Mapped[Project] = relationship(back_populates="cablings")

    __table_args__ = (
        UniqueConstraint(
            "project_id", "normalized_key", name="uq_cablings_project_normalized_key"
        ),
        Index("ix_cablings_project_endpoint", "project_id", "a_device", "b_device"),
    )


class PowerCabling(TimestampMixin, Base):
    __tablename__ = "power_cablings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    a_device: Mapped[str] = mapped_column(String(255), nullable=False)
    a_port: Mapped[str] = mapped_column(String(255), nullable=False)
    a_port_type: Mapped[str] = mapped_column(String(64), nullable=False)
    b_device: Mapped[str] = mapped_column(String(255), nullable=False)
    b_port: Mapped[str] = mapped_column(String(255), nullable=False)
    b_port_type: Mapped[str] = mapped_column(String(64), nullable=False)
    bank: Mapped[str] = mapped_column(String(64), nullable=False)
    outlet: Mapped[str] = mapped_column(String(64), nullable=False)
    cable_type: Mapped[str | None] = mapped_column(String(64))
    label: Mapped[str | None] = mapped_column(String(255))
    length: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)
    normalized_key: Mapped[str] = mapped_column(String(1024), nullable=False)

    project: Mapped[Project] = relationship(back_populates="power_cablings")

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "normalized_key",
            name="uq_power_cablings_project_normalized_key",
        ),
        Index(
            "ix_power_cablings_project_endpoint", "project_id", "a_device", "b_device"
        ),
    )


class TemplateSet(TimestampMixin, Base):
    __tablename__ = "template_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    sections: Mapped[list[TemplateSection]] = relationship(
        back_populates="template_set", cascade="all, delete-orphan"
    )


class TemplateSection(TimestampMixin, Base):
    __tablename__ = "template_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_set_id: Mapped[int] = mapped_column(
        ForeignKey("template_sets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    section_order: Mapped[int] = mapped_column(Integer, nullable=False)
    output_targets: Mapped[str] = mapped_column(Text, nullable=False)
    applicable_roles: Mapped[str | None] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    template_set: Mapped[TemplateSet] = relationship(back_populates="sections")

    __table_args__ = (
        UniqueConstraint(
            "template_set_id",
            "category",
            "section_order",
            name="uq_template_sections_set_category_order",
        ),
        Index(
            "ix_template_sections_order", "template_set_id", "category", "section_order"
        ),
    )


class TemplateSetSnapshot(TimestampMixin, Base):
    __tablename__ = "template_set_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_template_set_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))

    project: Mapped[Project] = relationship(back_populates="template_snapshots")
    sections: Mapped[list[SectionSnapshot]] = relationship(
        back_populates="template_set_snapshot", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "source_template_set_id",
            name="uq_template_snapshot_project_source",
        ),
    )


class SectionSnapshot(TimestampMixin, Base):
    __tablename__ = "section_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_set_snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("template_set_snapshots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    section_order: Mapped[int] = mapped_column(Integer, nullable=False)
    output_targets: Mapped[str] = mapped_column(Text, nullable=False)
    applicable_roles: Mapped[str | None] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    template_set_snapshot: Mapped[TemplateSetSnapshot] = relationship(
        back_populates="sections"
    )
    application_rules: Mapped[list[SectionApplicationRule]] = relationship(
        back_populates="section_snapshot",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "ix_section_snapshots_order",
            "template_set_snapshot_id",
            "category",
            "section_order",
        ),
    )


class SectionApplicationRule(TimestampMixin, Base):
    __tablename__ = "section_application_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    section_snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("section_snapshots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    filters_json: Mapped[str | None] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="section_application_rules")
    section_snapshot: Mapped[SectionSnapshot] = relationship(
        back_populates="application_rules"
    )

    __table_args__ = (
        UniqueConstraint(
            "project_id", "section_snapshot_id", name="uq_section_rule_project_section"
        ),
    )


class ArtifactVersion(TimestampMixin, Base):
    __tablename__ = "artifact_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    mode: Mapped[str] = mapped_column(String(32), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(512), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)
    success_word: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    success_excel: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    success_image: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    errors_json: Mapped[str | None] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="artifact_versions")
    files: Mapped[list[ArtifactFile]] = relationship(back_populates="artifact_version")
    diff_reports_from: Mapped[list[DiffReport]] = relationship(
        back_populates="from_version",
        foreign_keys=lambda: [DiffReport.from_version_id],
    )
    diff_reports_to: Mapped[list[DiffReport]] = relationship(
        back_populates="to_version",
        foreign_keys=lambda: [DiffReport.to_version_id],
    )

    __table_args__ = (
        UniqueConstraint(
            "project_id", "version_number", name="uq_artifact_versions_project_version"
        ),
        UniqueConstraint(
            "project_id", "fingerprint", name="uq_artifact_versions_project_fingerprint"
        ),
        Index("ix_artifact_versions_project_created", "project_id", "created_at"),
    )


class ArtifactFile(TimestampMixin, Base):
    __tablename__ = "artifact_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    artifact_version_id: Mapped[int] = mapped_column(
        ForeignKey("artifact_versions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    artifact_type: Mapped[str] = mapped_column(String(32), nullable=False)
    relative_path: Mapped[str] = mapped_column(Text, nullable=False)

    artifact_version: Mapped[ArtifactVersion] = relationship(back_populates="files")

    __table_args__ = (
        UniqueConstraint(
            "artifact_version_id",
            "artifact_type",
            "relative_path",
            name="uq_artifact_files_unique",
        ),
    )


class DiffReport(TimestampMixin, Base):
    __tablename__ = "diff_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    from_version_id: Mapped[int] = mapped_column(
        ForeignKey("artifact_versions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    to_version_id: Mapped[int] = mapped_column(
        ForeignKey("artifact_versions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    summary: Mapped[str | None] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="diff_reports")
    from_version: Mapped[ArtifactVersion] = relationship(
        back_populates="diff_reports_from", foreign_keys=[from_version_id]
    )
    to_version: Mapped[ArtifactVersion] = relationship(
        back_populates="diff_reports_to", foreign_keys=[to_version_id]
    )
    items: Mapped[list[DiffItem]] = relationship(back_populates="diff_report")

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "from_version_id",
            "to_version_id",
            name="uq_diff_reports_project_pair",
        ),
    )


class DiffItem(TimestampMixin, Base):
    __tablename__ = "diff_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    diff_report_id: Mapped[int] = mapped_column(
        ForeignKey("diff_reports.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    artifact_type: Mapped[str] = mapped_column(String(32), nullable=False)
    location: Mapped[str] = mapped_column(Text, nullable=False)
    change_type: Mapped[str] = mapped_column(String(32), nullable=False)
    before_value: Mapped[str | None] = mapped_column(Text)
    after_value: Mapped[str | None] = mapped_column(Text)

    diff_report: Mapped[DiffReport] = relationship(back_populates="items")


class FieldChangeLog(TimestampMixin, Base):
    __tablename__ = "field_change_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(Integer)
    field_name: Mapped[str] = mapped_column(String(128), nullable=False)
    before_value: Mapped[str | None] = mapped_column(Text)
    after_value: Mapped[str | None] = mapped_column(Text)
    context: Mapped[str | None] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="field_change_logs")

    __table_args__ = (
        Index(
            "ix_field_change_logs_project_entity",
            "project_id",
            "entity_type",
            "entity_id",
        ),
    )
