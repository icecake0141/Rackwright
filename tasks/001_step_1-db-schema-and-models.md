# Task 001: 1 -- DB Schema and Models

## Step 1 -- DB Schema and Models

### Acceptance Criteria
- [ ] Measurable: Core tables/models (Project/Site/Room/Row/Rack/Device/Cabling/PowerCabling + template snapshot + artifact + diff + FieldChangeLog) are created and queryable with specified unique/index constraints.
- [ ] Verification: Run migration up/down test and schema constraint checks (`tests/test_migration_step1.py`).
- [ ] Evidence: Passing test output and migration files (`alembic/versions/20260225_0001_initial_schema.py`, `alembic/versions/20260225_0002_template_set_sources.py`).

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
