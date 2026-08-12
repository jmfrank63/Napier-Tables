# Integer Engine Task 3

Work only in the isolated implementation worktree. Read `02-integer-engine/README.md` first.

Implement bounded logarithm calculation in `src/napier_tables/integer_log.py`; use independent fixtures in `tests/fixtures/reference_values.py` and tests in `tests/test_integer_log.py`.

Symbols: private `_ln_bounds(value: int, scale: int) -> tuple[int, int]`; private `_ratio_bounds(value: int, base: int, scale: int) -> tuple[int, int]`; public `calculate_log_scaled(value: int, base: int, scale: int) -> int`.

- [ ] Write failing tests for `log_10(1)=0`, `log_10(10)=scale`, base 2 identities, and prepared base-10 values 2, 3, 100 at four digits.
- [ ] Run `python -m pytest tests/test_integer_log.py -k 'log_scaled or identity or reference' -q` and capture failure.
- [ ] Implement lower/upper convergence and one final integer rounding; reject value < 1, base < 2, and non-positive scale.
- [ ] Run focused/full suites, `rg 'math\.log|float\(' src`, and `git diff --check`.
- [ ] Commit `feat: calculate integer logarithms with bounded rounding` and report to `.superpowers/sdd/phase-02/task-3-report.md`.
