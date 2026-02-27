"""
Copyright 2026 Rackwright Contributors
SPDX-License-Identifier: Apache-2.0

This file was created or modified with the assistance of an AI (Large Language Model).
Review required for correctness, security, and licensing.
"""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TemplateSetRecord(Base):
    __tablename__ = "template_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    sections: Mapped[list[TemplateSectionRecord]] = relationship(
        back_populates="template_set", cascade="all, delete-orphan"
    )


class TemplateSectionRecord(Base):
    __tablename__ = "template_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_set_id: Mapped[int] = mapped_column(
        ForeignKey("template_sets.id", ondelete="CASCADE"), nullable=False
    )
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    section_order: Mapped[int] = mapped_column(Integer, nullable=False)
    output_targets: Mapped[str] = mapped_column(Text, nullable=False)
    applicable_roles: Mapped[str | None] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    template_set: Mapped[TemplateSetRecord] = relationship(back_populates="sections")

    __table_args__ = (
        UniqueConstraint(
            "template_set_id",
            "category",
            "section_order",
            name="uq_template_sections_set_category_order",
        ),
    )


class ProjectRecord(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    owner: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    template_snapshots: Mapped[list[TemplateSetSnapshotRecord]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    section_application_rules: Mapped[list[SectionApplicationRuleRecord]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class TemplateSetSnapshotRecord(Base):
    __tablename__ = "template_set_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    source_template_set_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))

    project: Mapped[ProjectRecord] = relationship(back_populates="template_snapshots")
    sections: Mapped[list[SectionSnapshotRecord]] = relationship(
        back_populates="template_set_snapshot", cascade="all, delete-orphan"
    )


class SectionSnapshotRecord(Base):
    __tablename__ = "section_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_set_snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("template_set_snapshots.id", ondelete="CASCADE"), nullable=False
    )
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    section_order: Mapped[int] = mapped_column(Integer, nullable=False)
    output_targets: Mapped[str] = mapped_column(Text, nullable=False)
    applicable_roles: Mapped[str | None] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    template_set_snapshot: Mapped[TemplateSetSnapshotRecord] = relationship(
        back_populates="sections"
    )
    application_rules: Mapped[list[SectionApplicationRuleRecord]] = relationship(
        back_populates="section_snapshot", cascade="all, delete-orphan"
    )


class SectionApplicationRuleRecord(Base):
    __tablename__ = "section_application_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    section_snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("section_snapshots.id", ondelete="CASCADE"), nullable=False
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    filters_json: Mapped[str | None] = mapped_column(Text)

    project: Mapped[ProjectRecord] = relationship(
        back_populates="section_application_rules"
    )
    section_snapshot: Mapped[SectionSnapshotRecord] = relationship(
        back_populates="application_rules"
    )

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "section_snapshot_id",
            name="uq_section_rule_project_section",
        ),
    )
