# Integer Engine Task 4

Work only in the isolated implementation worktree. Read `02-integer-engine/README.md` first.

Implement `calculate_row(value: int, base: int, fractional_digits: int) -> LogRow` in `src/napier_tables/integer_log.py`; test in `tests/test_integer_log.py`.

- [ ] Write failing tests for `calculate_row(3, 10, 4)` and invalid value/base/precision.
- [ ] Run `python -m pytest tests/test_integer_log.py -q` and capture failure.
- [ ] Derive `scale=10**fractional_digits`, call `calculate_log_scaled`, construct the Phase 1 `LogRow`.
- [ ] Run focused/full suites and `git diff --check`.
- [ ] Commit `feat: expose logarithm row calculation` and report to `.superpowers/sdd/phase-02/task-4-report.md`.
