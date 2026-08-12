# Integer Engine Task 2

Work only in the isolated implementation worktree. Read `02-integer-engine/README.md` first.

Implement exact range reduction and bounded atanh helpers in `src/napier_tables/integer_log.py`; tests in `tests/test_integer_log.py`.

Symbols: private `_reduce_ratio(numerator: int, denominator: int) -> tuple[int, int, int]`; private `_atanh_bounds(numerator: int, denominator: int, terms: int) -> tuple[Fraction, Fraction]`.

- [ ] Write failing tests for unity, exact powers of two, reciprocal ratios, normalized `[1, 2)` invariant, and independent first-term ln fixtures.
- [ ] Run `python -m pytest tests/test_integer_log.py -k 'reduce or atanh' -q` and capture failure.
- [ ] Implement exact rational numerator/denominator arithmetic; no float/log calls.
- [ ] Run focused/full suites and `git diff --check`.
- [ ] Commit `feat: add bounded integer range reduction` and report to `.superpowers/sdd/phase-02/task-2-report.md`.
