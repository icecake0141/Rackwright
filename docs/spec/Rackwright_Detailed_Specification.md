**Rackwright -- Detailed Specification**

Version: 1.0 \| Date: 2026-02-25 \| Language: English

Purpose: Define the functional and non-functional requirements for
Rackwright, a Flask-based web tool that generates ZeroStage on-prem
deployment document sets from templates and project data.

# 1. Scope and Goals

## 1.1 In Scope

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Project-centric workflow: one document set per project
    (site/room/row/rack group).

-   Template-set based project creation (clone template project, then
    edit project data).

-   Server-side rendered web UI (Flask).

-   Dynamic preview from templates plus DB data; explicit generation
    step produces versioned artifacts.

-   Outputs: Word (.docx), Excel (.xlsx), and images (PNG/SVG).

-   Network cabling captured and exchanged via CSV import/export; power
    cabling captured via dedicated model and CSV.

-   Artifact versioning, diff reports, and in-document marking for
    Word/Excel.

-   Field-level change logging for project data and generated artifacts.

## 1.2 Out of Scope (Initial Release)

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Automated validation that a device must be redundant (power
    redundancy is inferred from actual power connections only).

-   Graphical network cabling diagram (future enhancement).

-   Photo upload/storage (tool generates submission instructions only).

-   Complex template DSL (loops/advanced logic); only limited
    conditional branching is allowed.

-   User authentication/authorization (all users can generate artifacts;
    confirmation dialog required).

-   Encryption at rest for stored secrets (device_vars may contain
    plaintext; document this risk).

# 2. Data Model Overview

Database: SQLite (SQLAlchemy ORM). Source of truth is the DB. YAML
import/export is a snapshot mechanism.

## 2.1 Hierarchy

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Site -\> Room -\> Row -\> Rack -\> RU -\> Device

-   Site is metadata-focused (address, entry procedure, contact info).

-   Device placement: rack_id + ru_start + ru_size (+ orientation).

## 2.2 Core Entities (Summary)

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

  -----------------------------------------------------------------------------
  Entity                  Key Fields (examples)         Notes
  ----------------------- ----------------------------- -----------------------
  Project                 name, owner, notes, revision  No status machine;
                                                        always editable.

  Rack                    name, rack_height_u, row_id   RU-accurate layout
                                                        required.

  Device                  name, role, model, serial,    Ports are strings;
                          power_watts, rack_id,         power ports treated
                          ru_start                      like other ports.

  Cabling                 a_device/a_port/a_port_type   A/B endpoints
                          \<-\> b\_\..., cable_type,    normalized.
                          label                         

  PowerCabling            device power port -\> PDU     PDU is a Device with
                          outlet + bank/outlet          role=PDU.

  TemplateSetSnapshot     source_template_set_id,       Created at project
                          project_id                    creation; immutable.

  SectionSnapshot         target_type, category, order, Unit of templating;
                          output_targets, text          stored as rows.

  ArtifactVersion         version_number, mode,         Version number
                          fingerprint, success flags    auto-increments;
                                                        idempotent generation
                                                        via fingerprint.

  DiffReport              from_version, to_version,     Word+Excel diffs;
                          diff_items                    row/cell-level where
                                                        feasible.

  FieldChangeLog          entity_type/id, field,        Recorded via ORM
                          before/after, context         before_flush hook.
  -----------------------------------------------------------------------------

# 3. Templates

## 3.1 Template Format

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Section templates are Markdown documents containing Jinja2
    expressions.

-   Template granularity is section-level; documents are composed from
    ordered sections.

-   Template reuse scope: within the same template set only.

## 3.2 Snapshot Policy

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   When a project is created from a template set, the template set is
    snapshotted into SectionSnapshot rows.

-   Project always uses its snapshot; later edits to the original
    template set do not affect existing projects.

## 3.3 Variable Scope and Control

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Jinja variable scope is limited to the section target object
    (Project/Rack/Device) plus shared project context.

-   Control structures: conditionals are allowed; advanced loops/complex
    logic is discouraged and should be handled via precomputed views.

## 3.4 Output Targets

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Each SectionSnapshot declares output_targets: word/excel/image.

-   Template set statically defines which sections go to which artifact
    type.

## 3.5 Project-side Filters

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Section expansion supports per-project filters (simple UI) such as
    role and rack scope.

-   Filters are stored on the project, not in templates.

# 4. Cabling CSV Specifications

## 4.1 Network Cabling CSV (Connections)

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

Merge semantics: update/add by normalized endpoint key; do not delete
unspecified rows.

-   Required columns: a_device, a_port, a_port_type, b_device, b_port,
    b_port_type

-   Recommended: cable_type, label

-   Optional: length, notes

-   Port type initial values: dcim.interface, dcim.frontport,
    dcim.rearport

## 4.2 Power Cabling CSV

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Required columns: a_device, a_port, a_port_type, b_device, b_port,
    b_port_type, bank, outlet

-   Recommended: cable_type, label

-   Optional: length, notes

-   Port type initial values: dcim.powerport, dcim.poweroutlet

-   b_device typically references a Device with role=PDU.

## 4.3 Unknown Devices on Import

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Import performs a dry-run to detect unknown device names.

-   UI prompts the user to confirm creating placeholder devices
    before applying changes.

-   Network cabling CSV: unknown devices are created as placeholders
    with `role="Other"` (unplaced).

-   Power cabling CSV: unknown b_device placeholders are created with
    `role="PDU"` (unplaced); other unknown power-side devices default
    to `role="Other"`.

### 4.4 Unknown-device role assignment policy (normative)

-   Network cabling CSV import:
    unknown device placeholder role MUST be `"Other"`.

-   Power cabling CSV import:
    unknown `b_device` placeholder role MUST be `"PDU"`.

-   Power cabling CSV import (other unknown devices):
    placeholder role MUST be `"Other"`.

-   Change log context includes csv_import + file name + row number.

# 5. Generation and Artifacts

## 5.1 Generation Modes

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   All: generate Word + Excel + images in one run.

-   ByType: generate Word only, Excel only, or images only.

-   Generation is triggered explicitly by the user; preview remains
    dynamic.

## 5.2 Idempotency and Fingerprints

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Generation computes a fingerprint from: relevant project data
    subset, generation mode, and diff-base version selection.

-   If the fingerprint matches a previous generation, generation is
    skipped and the existing artifact version is returned.

## 5.3 Partial Failure Handling

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   ArtifactVersion is created even if some artifact types fail.

-   Success flags and structured errors are stored; failed types remain
    absent.

-   A new artifact version is required for re-generation (no in-place
    re-run for the same version).

## 5.4 Storage Layout

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

Artifacts are stored on filesystem. Base directory defaults to ./data
and can be overridden via RACKWRIGHT_DATA_DIR.

Path pattern:
/projects/{project_id}/versions/{version_number}/{artifact_type}/\<files\>

# 6. Diff and Marking

## 6.1 Comparison

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   User selects any past artifact version as the comparison base.

-   Diff targets: Word and Excel (images excluded).

## 6.2 Granularity

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Excel: row/cell-level diffs where feasible; otherwise fallback to
    sheet-level notes.

-   Word: section/paragraph-level mapping as feasible; otherwise
    fallback to text-run-level heuristics.

## 6.3 Outputs

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Diff report is produced in two forms: (1) Excel diff list, (2) Word
    diff summary.

-   In-document marking: highlight + comment insertion in Word; cell
    highlighting/comment equivalents in Excel where feasible.

-   Diffs are retained for the same lifetime as artifact versions.

# 7. UI (High-level)

-   Dashboard: project list + create-from-template + recent versions.

-   Project detail default tab: hierarchy tree with basic edits and
    navigation.

-   Project detail provides direct edit controls for Site/Room/Row names
    (and Site metadata fields).

-   Device tabs: Basics / Cabling / Power / Settings / Config Blocks.

-   Rack tabs: Basics / Layout / Power.

-   Project-level Cabling page: table editor + CSV import/export +
    filters (rack/row/device).

-   Generation dialog: mode selection (All/ByType), remarks, base
    version for diff; conflict handling with
    stop/force/save-and-regenerate choices.

-   Project-level section rules editor provides per-section enabled flag
    and simple role/rack-scope filter editing.

# 8. Non-functional Requirements

-   Deterministic outputs for a given fingerprint.

-   Traceability: field change logs, generation logs, error jump targets
    (section or CSV row).

-   Performance target: projects up to hundreds of devices and thousands
    of cabling rows should remain interactive (CSV import/export
    primary).

-   Security note: plaintext device_vars allowed in initial release;
    document and warn prominently.

# 9. Acceptance Criteria (Initial Release)

1.  User can create a project from a template set snapshot and edit
    hierarchy data.

2.  User can import/export network cabling and power cabling via CSV
    with merge semantics and endpoint normalization.

3.  User can generate Word and Excel artifacts; artifacts are versioned
    and stored on filesystem.

4.  User can compare any two artifact versions and obtain a diff Excel +
    diff Word; Word marking includes highlight + comments.

5.  User can view generation errors and navigate to the referenced
    section or CSV row.

6.  Field-level change logs are recorded for edits and imports.