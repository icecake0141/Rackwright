# Task 008: 8 -- Web UI (Server-side)

## Step 8 -- Web UI (Server-side)

### Acceptance Criteria
- [x] Measurable: Server-side UI provides dashboard/project/rack/device/cabling/generate/versions/errors flows with CSV import-export, conflict actions, and jump navigation.
- [x] Verification: Execute UI integration tests for core flows, filters, hierarchy display, and conflict behavior (`tests/test_web_ui_step8.py`).
- [x] Evidence: `rackwright/app.py`, `rackwright/templates/*.html`, and passing UI test output.

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
- [x] Measurable: Schema migrates cleanly and change logs are produced for edit/import flows with unique key enforcement.
- [x] Verification: Run migration + change logging + CSV normalization tests.
- [x] Evidence: `tests/test_migration_step1.py`, `tests/test_change_logging_step2.py`, `tests/test_csv_services_step3.py` results.

-   All migrations apply on empty DB.

-   Change logs recorded for edits and CSV imports.

-   Uniq constraints prevent duplicate cabling keys post-normalization.

## Gate B -- CSV Workflow

### Acceptance Criteria
- [x] Measurable: CSV import/export follows required schema; unknown-device confirmation and merge-no-delete behavior are enforced.
- [x] Verification: Run CSV service + UI CSV flow tests.
- [x] Evidence: `tests/test_csv_services_step3.py`, `tests/test_web_ui_step8.py` outputs.

-   CSV export matches schema.

-   CSV import dry-run identifies unknown devices and requires user
    confirmation.

-   Merge updates existing rows and adds new rows without deleting
    unspecified rows.

## Gate C -- Generation

### Acceptance Criteria
- [x] Measurable: Generation writes DB metadata + filesystem artifacts for all/by-type, keeps idempotency, and records partial-failure errors.
- [x] Verification: Run generation and UI generation tests.
- [x] Evidence: `tests/test_generation_step6.py`, `tests/test_web_ui_step8.py` outputs and generated files under `data/projects/...`.

-   All/ByType generation produces filesystem artifacts and DB metadata
    rows.

-   Idempotent re-run returns existing version for identical
    fingerprint.

-   Partial failure stores structured errors and allows navigation to
    fix points.

## Gate D -- Diff

### Acceptance Criteria
- [x] Measurable: Diff generation between versions outputs Excel+Word diff artifacts with persisted itemized changes.
- [x] Verification: Run diff unit/integration test with known modified cell/text.
- [x] Evidence: `tests/test_diff_step7.py` output and generated diff files.

-   Diff between any two versions produces diff Excel list and Word
    summary.

-   Word contains highlight + comment marking for changed content when
    possible.

-   Excel marks changed cells and lists them in the diff sheet.

## Gate E -- UI

### Acceptance Criteria
- [x] Measurable: Main pages respond without 500 errors, downloads and jump links function, and core routes are covered by automated tests.
- [x] Verification: Run web UI integration tests and smoke requests.
- [x] Evidence: `tests/test_web_ui_step8.py` output and gate execution records.

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
