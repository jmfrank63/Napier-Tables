# Integer Engine Task 1

Work only in the isolated implementation worktree. Read `02-integer-engine/README.md` first.

Implement integer rounding/formatting in `src/napier_tables/integer_log.py` with tests in `tests/test_integer_log.py`.

Symbols: `round_ratio(numerator: int, denominator: int, scale: int) -> int`; `scaled_to_text(scaled_value: int, fractional_digits: int) -> str`.

- [ ] Write failing tests for thirds, exact halves using documented half-up behavior, negative numerators, zero denominator, `3010 -> "0.3010"`, leading zero, and negative text.
- [ ] Run `python -m pytest tests/test_integer_log.py -k 'round or text' -q` and capture failure.
- [ ] Implement with integer quotient/remainder arithmetic only; reject invalid denominator/precision.
- [ ] Run focused and full suites plus `git diff --check`.
- [ ] Commit `feat: add integer rounding and formatting` and report to `.superpowers/sdd/phase-02/task-1-report.md`.
