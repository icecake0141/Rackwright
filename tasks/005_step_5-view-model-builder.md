# Task 005: 5 -- View Model Builder

## Step 5 -- View Model Builder

### Acceptance Criteria
- [x] Measurable: Deterministic Python-side view builders return ordered/filtered structures for rack devices, project cablings, and rack power cablings.
- [x] Verification: Execute view builder determinism/content tests (`tests/test_view_builders_step5.py`).
- [x] Evidence: `rackwright/view_builders.py` and passing test output.

23. Implement view builders: devices_in_rack, cablings_for_project,
    power_cablings_for_rack, etc.

24. Ensure these are computed in Python prior to template rendering (not
    in Jinja).

25. Add unit tests for view content and determinism.
