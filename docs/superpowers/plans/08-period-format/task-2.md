# Period Format Task 2

Work only in the isolated implementation worktree. Read `08-period-format/README.md` first.

Implement the period notation formatter in `src/napier_tables/period.py` with tests in `tests/test_period.py`.

Symbols: `format_period_log(scaled_value: int, fractional_digits: int, rounded_up: bool) -> str`; `difference_text(current_scaled: int, next_scaled: int) -> str`.

Conventions (fixed by the design spec): characteristic = `scaled_value // 10**fractional_digits` (floor division; the mantissa is always non-negative), printed once and separated from the mantissa by a comma; a comma after every fifth mantissa digit, as Briggs and Vlacq printed (e.g. `0,30102,99957`); each digit of a negative characteristic's absolute value followed by U+0305 (vinculum); the final mantissa digit followed by U+0323 (combining dot below) when `rounded_up` is true. The rounding mark is a deliberate project convention adopted from Babbage (1827), outside the cited period — never describe it as a period convention. `difference_text` returns `str(next_scaled - current_scaled)` — units of the last place.

- [ ] Write failing tests asserting exact strings: `"0,3010"` for `(3010, 4, False)`; `"0,8451" + "̣"` for `(8451, 4, True)`; `"0,30102,99957" + "̣"` for `(3010299957, 10, True)`; `"1" + "̅" + ",6990"` for `(-3010, 4, False)`; `difference_text(3010, 4771) == "1761"`.
- [ ] Run `python -m pytest tests/test_period.py -k notation -q` and capture failure.
- [ ] Implement both functions with integer arithmetic and string assembly only; no floats, no engine calls.
- [ ] Run focused and full suites plus `git diff --check`.
- [ ] Commit `feat: format logarithms in period notation` and report to `.superpowers/sdd/phase-08/task-2-report.md`.
