# Task 001: 1 -- DB Schema and Models

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
