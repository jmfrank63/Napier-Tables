# Historical Format Task 1

Work only in the isolated implementation worktree. Read `07-historical-format/README.md` first.

Implement the N-resolution → fixed-decade mapping and `HistoricalConfig` validation in `src/napier_tables/historical.py` with tests in `tests/test_historical.py`.

Symbols: `class HistoricalConfig` (frozen, slots) with `resolution: int` (≥ 0), `log_precision: int` (≥ 1), `base: int = 10`, and `validate() -> None`; `decade_range(resolution: int) -> tuple[int, int]`.

Decade rule (fixed, upper bound exclusive): `decade_range(r) == (10**r, 10**(r+1))`. The upper bound is the stop value for the generator, so `range(*decade_range(r))` never yields `10**(r+1)`. This matches the referenced 1950s log tables that cover 1–10, 10–100, 100–1000, … with the last 10/100/1000 excluded.

- [ ] Write failing tests for `decade_range(0) == (1, 10)`, `decade_range(1) == (10, 100)`, `decade_range(2) == (100, 1000)`, that `range(*decade_range(1))` yields 10–99 (100 excluded), and that `HistoricalConfig(resolution=-1, ...)` and `HistoricalConfig(log_precision=0, ...)` raise.
- [ ] Run `python -m pytest tests/test_historical.py -k 'range or config' -q` and capture failure.
- [ ] Implement `decade_range` and `HistoricalConfig.validate()` using integer power only; no floats.
- [ ] Run focused and full suites plus `git diff --check`.
- [ ] Commit `feat: map N resolution to fixed log-table decade` and report to `.superpowers/sdd/phase-07/task-1-report.md`.