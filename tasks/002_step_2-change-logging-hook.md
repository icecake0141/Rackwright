# Task 002: 2 -- Change Logging Hook

## Step 2 -- Change Logging Hook

### Acceptance Criteria
- [ ] Measurable: `before_flush` logs scalar field changes for new/dirty/deleted tracked entities with correct before/after values.
- [ ] Verification: Execute change logging tests covering web/csv/generate contexts (`tests/test_change_logging_step2.py`).
- [ ] Evidence: `rackwright/change_logging.py` implementation and passing test result.

9.  Implement a SQLAlchemy session event (before_flush) that detects
    dirty/new/deleted objects.

10. For tracked entities, emit FieldChangeLog rows for changed scalar
    fields (before/after).

11. Ensure context support: web edits vs csv_import(file,row) vs
    generate(mode).

12. Add unit tests: a field change produces exactly one log entry with
    correct before/after.
