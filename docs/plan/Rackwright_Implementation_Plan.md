**Rackwright -- Step-by-Step Implementation Plan**

Version: 1.0 \| Date: 2026-02-25 \| Language: English

Objective: Provide an implementation sequence suitable for a
code-generation agent, including test design, implementation steps, and
verification gates.

# 0. Conventions

-   Use trunk-based development with small, reviewable commits (or PRs).

-   Maintain a single configuration file for environment variables
    (development).

-   Treat the DB as source of truth; YAML is import/export only.

-   Keep generation deterministic; avoid non-deterministic timestamps
    inside artifacts unless explicitly required.

# 1. Project Setup

## 1.1 Repository Layout

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   app/ (Flask app package)

-   app/models/ (SQLAlchemy models)

-   app/views/ (Flask routes / blueprints)

-   app/services/ (generation, diff, csv import/export, logging)

-   app/templates/ (Jinja HTML templates)

-   app/static/ (CSS/JS)

-   tests/ (unit + integration)

-   data/ (default artifacts root; gitignored)

## 1.2 Dependencies

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Flask, SQLAlchemy, Alembic

-   python-docx (Word output and marking)

-   openpyxl (Excel output and marking)

-   Jinja2 (template rendering; already included via Flask)

-   pytest (test runner)

-   pandas (optional; convenient for CSV workflows)

# 2. Test Strategy (Design First)

## 2.1 Unit Tests

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Endpoint normalization: A/B ordering using (device_name, port_type,
    port_name).

-   CSV merge semantics: add/update behavior; ensure no deletion of
    absent rows.

-   Fingerprint computation: stable across runs; changes only when
    relevant subset changes.

-   Template expansion filters: role and rack filters behave as
    expected.

-   Diff extraction primitives: Excel cell diff; Word paragraph/run diff
    heuristics (minimal).

## 2.2 Integration Tests

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   DB migrations apply cleanly; model constraints enforced (unique
    keys).

-   CSV import dry-run finds unknown devices; confirm path creates
    placeholders.

-   Generation produces expected file set and writes
    ArtifactVersion/ArtifactFile rows.

-   Diff generation between two versions produces diff artifacts and
    DiffReport records.

## 2.3 System Tests (Minimal E2E)

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Create project -\> edit devices -\> import cabling -\> generate all
    -\> compare versions -\> download artifacts.

-   Error path: intentionally break a template -\> generate -\> verify
    UI shows error and jump target.

## 2.4 Test Data Fixtures

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Minimal template set snapshot with 3-5 sections across
    Project/Rack/Device.

-   Sample project with: 2 racks, 6 devices (including 1 PDU), 8 network
    cables, 6 power cables.

-   CSV files for network/power matching the schemas.

# 3. Implementation Steps

## Step 1 -- DB Schema and Models

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

1.  Define SQLAlchemy Base + TimestampMixin (created_at/updated_at).

2.  Implement models: Project, Site, Room, Row, Rack, Device, Cabling,
    PowerCabling.

3.  Implement template snapshot models: TemplateSetSnapshot,
    SectionSnapshot, SectionApplicationRule.

4.  Implement artifact models: ArtifactVersion, ArtifactFile,
    DiffReport, DiffItem.

5.  Implement FieldChangeLog model.

6.  Add relationships and cascades: hierarchy CASCADE; artifacts/diffs
    RESTRICT; project soft delete flag.

7.  Add unique constraints and indexes as specified.

8.  Create Alembic migration and verify migrate up/down in tests.

## Step 2 -- Change Logging Hook

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

9.  Implement a SQLAlchemy session event (before_flush) that detects
    dirty/new/deleted objects.

10. For tracked entities, emit FieldChangeLog rows for changed scalar
    fields (before/after).

11. Ensure context support: web edits vs csv_import(file,row) vs
    generate(mode).

12. Add unit tests: a field change produces exactly one log entry with
    correct before/after.

## Step 3 -- CSV Import/Export Services

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

13. Implement CSV export for Cabling and PowerCabling with
    required/recommended columns.

14. Implement CSV import dry-run: parse and collect unknown
    a_device/b_device names.

15. Implement confirmation flow: if approved, create placeholder devices
    (role=Other, unplaced).

16. Implement merge: normalize endpoints, upsert by normalized key,
    update attributes.

17. Record change logs with context including file and row.

18. Add tests: merge does not delete; A/B order normalization prevents
    duplicates.

## Step 4 -- Template Snapshot Creation

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

19. Implement template set management (minimal): create/edit template
    sets and their sections (internal UI).

20. On project creation: clone sections into TemplateSetSnapshot +
    SectionSnapshot rows.

21. Ensure output_targets and applicable_roles are stored as JSON TEXT.

22. Implement project-side section rules (filters and enabled flag).

## Step 5 -- View Model Builder

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

23. Implement view builders: devices_in_rack, cablings_for_project,
    power_cablings_for_rack, etc.

24. Ensure these are computed in Python prior to template rendering (not
    in Jinja).

25. Add unit tests for view content and determinism.

## Step 6 -- Artifact Generation

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

26. Implement generation entrypoint: generate(project_id, mode,
    base_version_id, remarks).

27. Compute fingerprint from relevant subset + mode + base_version_id.

28. Idempotency: if fingerprint exists, return existing ArtifactVersion.

29. Render sections in order (category + order) with project-side
    filters.

30. Word: construct .docx with python-docx; add headings per category;
    insert rendered markdown as plain paragraphs initially (Phase 1).

31. Excel: construct .xlsx with openpyxl; create sheets for
    wiring/labels/checklists; populate from DB/CSV-derived data.

32. Images: generate rack layout as PNG or SVG (Phase 1 can be a simple
    table-like image or placeholder).

33. Persist to filesystem under project/version/type; create
    ArtifactFile rows.

34. Handle partial failures: store success flags and structured errors
    with jump targets.

## Step 7 -- Diff Generation and Marking

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

35. Implement diff(from_version, to_version) for Word and Excel
    artifacts.

36. Excel: compare sheets and cells; produce DiffItems for changed
    cells; generate diff Excel list; mark changed cells in output
    workbook.

37. Word: produce a conservative diff (section-based or
    paragraph-based); insert highlights and comments where mapping is
    confident; otherwise add summary notes.

38. Generate Word diff summary and Excel diff list; store as
    ArtifactFiles; create DiffReport and DiffItems.

39. Add tests with small fixtures: ensure a known cell change is
    detected and marked.

## Step 8 -- Web UI (Server-side)

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

40. Dashboard: list projects; create project from template; show latest
    artifact version.

41. Project detail: hierarchy tree with basic edits; links to
    Rack/Device pages.

42. Rack detail: Basics/Layout/Power tabs; RU placement editor
    (table-based).

43. Device detail: tabs (Basics/Cabling/Power/Settings/Config Blocks).

44. Cabling page: project-level table editor + CSV import/export +
    filters.

45. Generation page/dialog: mode selection, remarks, base version;
    conflict handling UI (stop/force/save-and-regenerate).

46. Versions page: list artifact versions with download links and
    compare action.

47. Error UI: show generation errors and jump to referenced section or
    CSV row.

# 4. Verification Gates

## Gate A -- Schema + Logging

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   All migrations apply on empty DB.

-   Change logs recorded for edits and CSV imports.

-   Uniq constraints prevent duplicate cabling keys post-normalization.

## Gate B -- CSV Workflow

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   CSV export matches schema.

-   CSV import dry-run identifies unknown devices and requires user
    confirmation.

-   Merge updates existing rows and adds new rows without deleting
    unspecified rows.

## Gate C -- Generation

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   All/ByType generation produces filesystem artifacts and DB metadata
    rows.

-   Idempotent re-run returns existing version for identical
    fingerprint.

-   Partial failure stores structured errors and allows navigation to
    fix points.

## Gate D -- Diff

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   Diff between any two versions produces diff Excel list and Word
    summary.

-   Word contains highlight + comment marking for changed content when
    possible.

-   Excel marks changed cells and lists them in the diff sheet.

## Gate E -- UI

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

-   All core flows work without JS-heavy logic (server-side).

-   Downloads for artifacts and diff reports function.

-   Jump-to-error navigation works for section targets and CSV row
    targets.

# 5. Deliverables

-   Running Flask app with SQLite DB and Alembic migrations.

-   Template set authoring UI (minimal) and project snapshot creation.

-   Artifact generation: Word/Excel/images (Phase 1 quality acceptable).

-   Diff generation: Word+Excel with marking + summary reports.

-   Automated test suite (unit + integration) runnable in CI.