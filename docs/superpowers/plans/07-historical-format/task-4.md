# Historical Format Task 4

Work only in the isolated implementation worktree. Read `07-historical-format/README.md` first.

Add the browser route to `src/napier_tables/webapp.py` with tests in `tests/test_webapp.py`.

The route exposes a `GET /historical` form (resolution + log precision + base fields) and a `POST /historical` htmx response returning the historical HTML fragment from `build_historical_table` + `render_historical_html`. Keep the existing `MAX_TABLE_ROWS` guard but apply it to the decade size `10**(r+1) - 10**r == 9 * 10**r`; an oversized decade returns a visible error instead of rendering.

- [ ] Write failing tests in `tests/test_webapp.py` for `GET /historical` returning the form, `POST /historical` with resolution=1 and log_precision=4 returning the historical fragment, and an oversized/out-of-range request returning a visible error (no table).
- [ ] Run `python -m pytest tests/test_webapp.py -k historical -q` and capture failure.
- [ ] Extend `webapp.py` with the route and form; reuse the new `historical` module; do not duplicate calculation logic.
- [ ] Run focused and full suites plus `git diff --check`.
- [ ] Commit `feat: serve historical log tables in the browser` and report to `.superpowers/sdd/phase-07/task-4-report.md`.