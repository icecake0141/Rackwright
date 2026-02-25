# Task 002: 2 -- Change Logging Hook

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
