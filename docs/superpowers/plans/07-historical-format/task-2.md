# Historical Format Task 2

Work only in the isolated implementation worktree. Read `07-historical-format/README.md` first.

Implement the proportional layout builder in `src/napier_tables/historical.py` with tests in `tests/test_historical.py`.

Symbols: `class ProportionalRow` (frozen, slots) with `argument: str`, `columns: tuple[str, ...]`; `class HistoricalTable` (frozen, slots) with `config: HistoricalConfig`, `rows: tuple[ProportionalRow, ...]`; `build_historical_table(config: HistoricalConfig) -> HistoricalTable`.

The builder must reuse the existing integer-only engine. For resolution `r` it generates `log_base(N)` for each `N` in `range(*decade_range(r))` via `generate_table`/`calculate_row`, groups rows by argument (the leading significant digits of N), and produces 10 sub-columns per argument row using `scaled_to_text` for the mantissa text. No interpolation/mean-difference columns are produced. `log_base(1) == 0` must appear; `10**(r+1)` must never be present.

- [ ] Write failing tests that `build_historical_table(HistoricalConfig(resolution=0, log_precision=4))` returns rows for arguments 1–9, each row has exactly 10 sub-columns, the `log_base(1) == 0` mantissa is present, and `N == 10` is absent.
- [ ] Run `python -m pytest tests/test_historical.py -k build -q` and capture failure.
- [ ] Implement `build_historical_table` reusing the engine; keep all arithmetic on scaled integers; do not call the calculation engine from the renderer.
- [ ] Run focused and full suites plus `git diff --check`.
- [ ] Commit `feat: build proportional historical log layout` and report to `.superpowers/sdd/phase-07/task-2-report.md`.