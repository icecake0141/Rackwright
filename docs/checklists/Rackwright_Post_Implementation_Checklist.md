**Rackwright -- Post-Implementation Checklist**

Version: 1.0 \| Date: 2026-02-25 \| Language: English

Purpose: Provide a verification checklist to be executed after the Codex
agent completes implementation, prior to internal release/use.

Execution record:
- See `docs/checklists/Rackwright_Gate_Execution_Record_2026-02-25.md` for measured evidence and status notes.

# 1. Repository and Packaging

-   README includes: setup, run, tests, configuration, data directory
    location.

-   All secrets/config are via environment variables; defaults
    documented.

-   Data directory is gitignored and not committed.

-   Dependencies are pinned or constrained (requirements.txt/pyproject).

# 2. Database and Migrations

-   Fresh install: migrations apply on empty DB without manual steps.

-   Upgrade path: migration from previous version works (if applicable).

-   Foreign keys enforce cascades/restricts as specified.

-   Unique constraints: (project_id, name) for racks/devices;
    cabling/power unique keys after normalization.

# 3. Change Logging (FieldChangeLog)

-   Edits via UI produce field-level logs with correct before/after
    values.

-   CSV import produces logs with context including file name and row
    number.

-   Generation actions produce logs with context generate(mode,
    version).

-   Logs are queryable per project and per entity.

# 4. CSV Workflows

## 4.1 Network Cabling CSV

### Acceptance Criteria
- [ ] Measurable condition: Network CSV export/import includes required columns and supports dry-run unknown detection + normalized upsert merge semantics.
- [ ] Validation method: Execute `tests/test_csv_services_step3.py` and UI import/export flow in `tests/test_web_ui_step8.py`.
- [ ] Completion artifacts: test output logs and sample generated network CSV from `/projects/{id}/cabling/export/network`.

-   Export includes required columns and preserves labels/types/notes if
    present.

-   Import dry-run identifies unknown devices; UI requires explicit
    confirmation to create placeholders.

-   Unknown network-device placeholders are created as role=Other
    (unplaced).

-   Merge updates existing connections; adds new; does not delete
    unspecified rows.

-   A/B normalization prevents duplicate entries when endpoints are
    swapped.

## 4.2 Power Cabling CSV

### Acceptance Criteria
- [ ] Measurable condition: Power CSV export/import includes `bank`/`outlet` and creates unknown `b_device` placeholders as `role=PDU` when confirmed.
- [ ] Validation method: Execute `tests/test_csv_services_step3.py::test_power_import_creates_unknown_b_device_as_pdu_role` and end-to-end power CSV import via UI.
- [ ] Completion artifacts: test output logs and exported power CSV from `/projects/{id}/cabling/export/power`.

-   Export includes bank and outlet fields.

-   Import supports PDU as Device (role=PDU) and can create missing PDU
    placeholders with confirmation.

-   Unknown b_device placeholders in power import are created as
    role=PDU.

-   Merge semantics match network cabling behavior.

# 5. Template Snapshot and Rendering

-   Project creation snapshots templates into SectionSnapshot rows.

-   Editing the source template set does not modify existing projects.

-   Section ordering is category + order; output_targets respected.

-   Variable scope is limited (target object + project context).

-   Conditionals render correctly; no advanced template logic required.

# 6. Artifact Generation

-   All mode: produces Word + Excel + images and stores
    ArtifactVersion + ArtifactFiles.

-   ByType mode: produces selected artifact type only; still creates an
    ArtifactVersion.

-   Fingerprint idempotency: identical inputs return existing version
    (no new version_number).

-   Partial failures: success flags set correctly; errors stored with
    jump targets; successful outputs remain downloadable.

-   Filesystem layout matches:
    /projects/{project_id}/versions/{version_number}/{type}/\...

# 7. Diff and Marking

-   User can compare any two versions (base selectable).

-   Diff artifacts generated: Excel diff list + Word diff summary.

-   Excel marking: changed cells highlighted and/or annotated; diff list
    contains sheet/row/col and before/after.

-   Word marking: highlights + comments for detected changes; summary
    includes counts and affected sections.

-   Diffs retained for all versions (no auto-prune).

# 8. Web UI -- Core Flows

-   Dashboard: create project from template; list projects; show latest
    version.

-   Project: hierarchy tree edit; navigate to rack/device pages.

-   Rack: tabs Basics/Layout/Power function and save correctly.

-   Device: tabs Basics/Cabling/Power/Settings/Config Blocks function
    and save correctly.

-   Cabling page: table edit + filters; CSV import/export works
    end-to-end.

-   Generation dialog: mode, remarks, base version selection; conflict
    UX includes stop/force/save-and-regenerate choices.

-   Version list: download artifacts; trigger diff compare; download
    diff outputs.

-   Error view: jump-to-section and jump-to-csv-row behaviors operate.

# 9. Performance and Reliability

-   CSV import handles at least thousands of rows without timeouts under
    expected deployment.

-   Generation time is acceptable for initial release (documented
    expectations).

-   No orphan files: deleting an artifact version (if supported) cleans
    up filesystem and DB consistently, or deletion is disabled.

-   Error messages are actionable and reference a precise location
    (section name or CSV row).

# 10. Security and Operational Notes

-   Plaintext storage of device_vars is documented with a visible
    warning in UI and README.

-   Artifacts directory permissions are documented.

-   No debug mode in production configuration guidance.

# 11. Release Readiness Gate

1.  All automated tests pass (unit + integration).

2.  Manual smoke test passes core flow: create project -\> import
    cabling -\> generate all -\> generate diff -\> download artifacts.

3.  No critical UI errors; no 500 responses on main pages.

4.  Artifacts open correctly in Word/Excel and markings are visible.

5.  Diff reports are readable and accurately reflect changes.

6.  Known limitations are documented.