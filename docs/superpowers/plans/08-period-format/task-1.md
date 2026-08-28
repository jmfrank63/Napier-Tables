# Period Format Task 1

Work only in the isolated implementation worktree. Read `08-period-format/README.md` first.

Expose the direction of the final rounding step from the integer engine and carry it on each row.

Symbols: `calculate_log_scaled_with_direction(value: int, base: int, scale: int) -> tuple[int, bool]` in `src/napier_tables/integer_log.py`; new field `rounded_up: bool = False` on `LogRow` in `src/napier_tables/models.py`, populated by `calculate_row`.

`scale` keeps the engine's existing meaning: it is the multiplier itself (`calculate_row` passes `10**fractional_digits`), **not** a digit count. Every formula below uses it as a multiplier.

Direction rule: the boolean is `True` iff the returned scaled value is strictly greater than the true logarithm (the final rounding raised the retained digits); exact and rounded-down values return `False`.

Exact-rational rule: `log_base(value)` is rational exactly when `value` and `base` are integer powers of a common integer `g` (`value == g**a`, `base == g**b`). Detect this up front with integer root extraction; the logarithm is then exactly `a / b`, so return `(round_ratio(a * scale, b, 1), rounded * b > a * scale)`. The `value == base**k` case is the `b == 1` special case and returns `(k * scale, False)`. This detection is mandatory for termination: the guard bounds straddle a rational logarithm indefinitely, so the loop below can never decide it.

`candidate_guard` convergence rule (irrational logarithms only): extend the existing doubling loop. At each guard level compute `factor = 10**guard_digits`, the bounds `lower, upper` at `scale * factor`, and the candidate `rounded = round_ratio(lower, factor, 1)`. Convergence for direction requires **both** `round_ratio(lower, factor, 1) == round_ratio(upper, factor, 1)` **and** that `candidate_guard = rounded * factor` lies strictly outside `[lower, upper]`: `candidate_guard > upper` means rounded up (`True`), `candidate_guard < lower` means rounded down (`False`). While `lower <= candidate_guard <= upper` the direction is undecided — double `guard_digits` and continue; raise `CalculationError` past `_MAX_GUARD_DIGITS` as the existing loop does. Irrational logarithms always escape the interval because it shrinks around a value that never equals `candidate_guard / factor`.

- [ ] Write failing tests in `tests/test_integer_log.py`, passing `scale` as a multiplier: exact powers — `calculate_log_scaled_with_direction(1, 10, 10_000) == (0, False)`, `calculate_log_scaled_with_direction(10, 10, 10_000) == (10_000, False)`, `calculate_log_scaled_with_direction(100, 10, 10_000) == (20_000, False)`, `calculate_log_scaled_with_direction(4, 2, 10_000) == (20_000, False)`; exact rationals via a common root — `calculate_log_scaled_with_direction(2, 4, 10_000) == (5_000, False)` (log₄2 = 1/2) and `calculate_log_scaled_with_direction(4, 8, 10_000) == (6_667, True)` (log₈4 = 2/3 rounds up); irrationals — `calculate_row(2, 10, 4).rounded_up is False` (0.30102999… rounds down to 0.3010), `calculate_row(7, 10, 4).rounded_up is True` (0.84509804… rounds up to 0.8451), `calculate_row(5, 10, 4).rounded_up is True` (0.69897000… rounds up to 0.6990).
- [ ] Run `python -m pytest tests/test_integer_log.py -k direction -q` and capture failure.
- [ ] Implement `calculate_log_scaled_with_direction` with the exact-rational detection and `candidate_guard` rule above, refactor `calculate_log_scaled` to delegate to it, and extend `LogRow`/`calculate_row`. The `rounded_up` default `False` must keep every existing construction and test green.
- [ ] Run focused and full suites plus `git diff --check`.
- [ ] Commit `feat: expose rounding direction on logarithm rows` and report to `.superpowers/sdd/phase-08/task-1-report.md`.
