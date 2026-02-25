# Task 006: 6 -- Artifact Generation

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
