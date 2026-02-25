# Task 004: 4 -- Template Snapshot Creation

## Step 4 -- Template Snapshot Creation

### Acceptance Criteria
- [ ] Measurable: Template set/section CRUD and project snapshot cloning create immutable `SectionSnapshot` rows with JSON TEXT fields and per-project rule rows.
- [ ] Verification: Run template snapshot tests including immutability and section rule update (`tests/test_template_snapshot_step4.py`).
- [ ] Evidence: `rackwright/template_services.py`, template set UI routes/templates, and passing tests.

19. Implement template set management (minimal): create/edit template
    sets and their sections (internal UI).

20. On project creation: clone sections into TemplateSetSnapshot +
    SectionSnapshot rows.

21. Ensure output_targets and applicable_roles are stored as JSON TEXT.

22. Implement project-side section rules (filters and enabled flag).
