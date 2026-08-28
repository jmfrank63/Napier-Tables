# Period Format Task 6

Work only in the isolated implementation worktree. Read `08-period-format/README.md` first.

Phase handoff: verify the whole suite and the Briggs exemplar in the browser.

- [ ] Run `python -m pytest -q` and confirm green.
- [ ] Run `git diff --check`.
- [ ] Manually verify the Briggs exemplar — base 10, 1–1000, 14 fractional digits, matching the 1617 *Logarithmorum Chiliades Prima* — renders through `POST /period` (or the `GET /period` form) in the browser: column-major fill, commas after every fifth mantissa digit, difference columns in units of the last place, and dot-below rounding marks on raised final digits. If 14-place generation is too slow for interactive use, record the timing in the report and additionally verify a 10-place render (Vlacq/Vega precision) — but the 14-place render must complete and be checked at least once.
- [ ] Commit `docs: record period format handoff` and report to `.superpowers/sdd/phase-08/task-6-report.md`.
