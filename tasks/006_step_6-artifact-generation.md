# Task 006: 6 -- Artifact Generation

## Step 6 -- Artifact Generation

### Acceptance Criteria
- [ ] Measurable: `generate()` supports all/by-type modes, fingerprint idempotency, versioned filesystem output, and partial-failure error persistence with jump targets.
- [ ] Verification: Run generation tests for all outputs, idempotency, filter scope, and partial failure handling (`tests/test_generation_step6.py`).
- [ ] Evidence: `rackwright/generation_service.py`, generated artifact paths under `data/projects/...`, and passing test output.

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
