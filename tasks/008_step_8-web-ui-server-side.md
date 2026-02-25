# Task 008: 8 -- Web UI (Server-side)

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
