# Task 007: 7 -- Diff Generation and Marking

## Step 7 -- Diff Generation and Marking

### Acceptance Criteria
- [ ] Measurable: Diff between two versions produces Excel diff list + Word diff summary and persists `DiffReport`/`DiffItem` records; changed Excel cells and Word paragraphs are marked.
- [ ] Verification: Run diff test with known content changes and assert both Excel and Word diff artifacts (`tests/test_diff_step7.py`).
- [ ] Evidence: `rackwright/diff_service.py`, diff artifacts (`diff_excel`, `diff_word`), and passing test output.

35. Implement diff(from_version, to_version) for Word and Excel
    artifacts.

36. Excel: compare sheets and cells; produce DiffItems for changed
    cells; generate diff Excel list; mark changed cells in output
    workbook.

37. Word: produce a conservative diff (section-based or
    paragraph-based); insert highlights and comments where mapping is
    confident; otherwise add summary notes.

38. Generate Word diff summary and Excel diff list; store as
    ArtifactFiles; create DiffReport and DiffItems.

39. Add tests with small fixtures: ensure a known cell change is
    detected and marked.
