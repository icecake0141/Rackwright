# Task 009: Field Operation Document Improvement Plan (English-only)

## Goal

Raise generated artifacts from "data summary" level to "field-executable work instruction" level.

## Scope Decisions (Confirmed)

- Initial implementation focus: **network cabling operations**.
- Language for generated operation documents: **English only**.
- Final target: expand coverage to **full ZeroStage operational scope** (not cabling-only).

---

## Phase 1 (Next Implementation Start): Cabling-Centric Field Execution Pack

### Step 1. Define Field-Executable Acceptance Criteria

1. Create a checklist of mandatory information required for on-site execution.
2. Define pass/fail criteria for each generated artifact (Word/Excel).
3. Add a gate rule: artifact fails if any mandatory section is missing.

Deliverables:
- `docs/checklists/` entry for field-executable artifact criteria.
- Testable requirement list referenced by automated tests.

### Step 2. Define Target Document Structure (English)

1. Define Word section structure:
   - Work Overview
   - Preconditions and Safety
   - Step-by-step Procedure
   - Post-work Verification
   - Rollback Procedure
2. Define Excel sheet structure:
   - `work_steps`
   - `cabling_matrix`
   - `verification_checklist`
   - `issue_log`
3. Lock column schema for each sheet (stable contract).

Deliverables:
- Document schema spec in `docs/spec/`.
- Stable output field list for tests.

### Step 3. Extend Template Design for Operational Content

1. Add template section categories for operational instructions.
2. Add metadata support for:
   - step order
   - prerequisite tags
   - verification item tags
   - rollback hints
3. Keep backward compatibility with existing templates.

Deliverables:
- Template category definitions and migration/update notes.
- Updated template management behavior (minimal UI impact).

### Step 4. Extend View Models for Execution Context

1. Build deterministic, ordered work-step view models from project data.
2. Add derived fields needed by operators:
   - endpoint location context
   - cable label priority
   - execution sequence number
3. Ensure output is stable across repeated runs with unchanged inputs.

Deliverables:
- View-model builder updates.
- Unit tests for ordering and completeness.

### Step 5. Upgrade Word Generation Logic

1. Render explicit numbered procedures from view models.
2. Include per-step expected outcome and verification method.
3. Add "Stop/Escalate" conditions for unsafe or invalid states.

Deliverables:
- Word output that can be followed as a procedure without external interpretation.
- Snapshot/content tests for mandatory sections and structure.

### Step 6. Upgrade Excel Generation Logic

1. Populate `work_steps` with ordered executable actions.
2. Populate `verification_checklist` with pass/fail criteria and evidence fields.
3. Populate `issue_log` template for in-field deviation recording.

Deliverables:
- Excel workbook with operator-usable sheets (not summary-only).
- Tests validating required sheets/columns and non-empty critical rows.

### Step 7. Introduce Field-Readiness Validation Tests

1. Add automated checks for required Word sections.
2. Add automated checks for required Excel sheets and columns.
3. Add "no critical omission" assertions against realistic fixture data.

Deliverables:
- New test module for field-readiness validation.
- CI integration for these checks.

### Step 8. Practical Trial and Evidence Recording

1. Generate artifacts from a realistic sample project.
2. Perform desk review using field-readiness checklist.
3. Store findings and gap list under `evidence/` and checklists.

Deliverables:
- Updated evidence records.
- Decision on readiness for broader scope expansion.

---

## Phase 2 (Expansion): Full ZeroStage Operational Coverage

### Step 9. Domain Expansion Plan

Extend document generation coverage from network cabling to full ZeroStage operation domains, including (at minimum):

1. Power operation procedures (PDU feed, bank/outlet actions, safety constraints).
2. Rack/device physical operation steps (placement/orientation/RU validation).
3. Cutover and rollback orchestration across dependent tasks.
4. Site access and operational control requirements.
5. Post-implementation audit and handover package.

Deliverables:
- Incremental roadmap with domain-by-domain acceptance criteria.
- Cross-domain integration test scenarios.

---

## Acceptance Criteria for Task 009 (Planning Completion)

- [x] Plan is stored under `tasks/`.
- [x] Plan is written in English.
- [x] Initial implementation focus is cabling-centric.
- [x] Final roadmap explicitly includes full ZeroStage operational coverage.
- [x] Steps are implementation-ready and test-oriented.
