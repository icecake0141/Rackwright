# Task 003: 3 -- CSV Import/Export Services

## Step 3 -- CSV Import/Export Services

### Acceptance Criteria
- [x] Measurable: Network/Power CSV import-export supports required columns, dry-run unknown detection, placeholder creation roles, and normalized upsert merge semantics.
- [x] Verification: Run CSV service tests for merge/no-delete/normalization/context and power PDU placeholder behavior (`tests/test_csv_services_step3.py`).
- [x] Evidence: `rackwright/csv_services.py` and passing test output.

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
