# Historical Format Task 3

Work only in the isolated implementation worktree. Read `07-historical-format/README.md` first.

Implement the historical HTML fragment renderer in `src/napier_tables/historical.py` with tests in `tests/test_historical.py`.

Symbol: `render_historical_html(table: HistoricalTable, title: str | None = None) -> str`.

The renderer returns a deterministic, escaped `<table>` fragment for the browser: argument column, sub-column headers, one `<tr>` per `ProportionalRow`, mantissa text from `scaled_to_text`, and the leading characteristic shown once per row. No interpolation/mean-difference columns are rendered. It must use `html.escape`, deterministic attribute ordering, and must not call the calculation engine.

- [ ] Write failing tests requiring escaped title/config text, a `<table>` with argument and sub-column headers, one `<tr>` per `ProportionalRow`, exact mantissa text from `scaled_to_text`, and byte-stable repeated renders.
- [ ] Run `python -m pytest tests/test_historical.py -k render -q` and capture failure.
- [ ] Implement `render_historical_html` using `html.escape` and stable ordering.
- [ ] Run focused and full suites plus `git diff --check`.
- [ ] Commit `feat: render historical log tables as HTML` and report to `.superpowers/sdd/phase-07/task-3-report.md`.