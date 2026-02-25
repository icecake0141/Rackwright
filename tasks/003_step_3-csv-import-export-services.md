# Task 003: 3 -- CSV Import/Export Services

## Step 3 -- CSV Import/Export Services

### Acceptance Criteria
- [ ] Criteria 1: Define measurable condition for this section.
- [ ] Criteria 2: Include validation method (test, review, or evidence).
- [ ] Criteria 3: State completion artifacts (files, screenshots, outputs).

13. Implement CSV export for Cabling and PowerCabling with
    required/recommended columns.

14. Implement CSV import dry-run: parse and collect unknown
    a_device/b_device names.

15. Implement confirmation flow: if approved, create placeholder devices
    (Network: role=Other, unplaced; Power: unknown b_device as
    role=PDU, unplaced).

16. Implement merge: normalize endpoints, upsert by normalized key,
    update attributes.

17. Record change logs with context including file and row.

18. Add tests: merge does not delete; A/B order normalization prevents
    duplicates.
