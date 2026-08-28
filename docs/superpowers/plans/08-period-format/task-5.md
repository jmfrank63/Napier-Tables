# Period Format Task 5

Work only in the isolated implementation worktree. Read `08-period-format/README.md` first.

Integrate the period table into the browser via `src/napier_tables/webapp.py`.

Routes: `GET /period` renders a form (base, start, end, log precision, rows per column, columns per page, differences checkbox) inside the existing page shell; `POST /period` returns the period HTML fragment for htmx swaps and the full page shell for non-htmx requests. Reuse `build_period_table` + `render_period_html`. Keep the `MAX_TABLE_ROWS` guard applied to `end - start + 1`, rejected with a visible error rather than a truncated table. Malformed and invalid field values abort with 400.

Every configurable behavior the route promises must have its own test:

- [ ] Write failing tests in `tests/test_webapp.py`:
  - `GET /period` returns the form with all six fields and the differences checkbox.
  - `POST /period` (htmx) with base 10, 1–100, 4 digits returns a fragment containing `Numerus` and a known period-notation cell.
  - `rows_per_column` moves the column boundary: 1–100 with `rows_per_column=10` puts value 11 at the top of the second column group (assert the first column's cells end at 10 and the second's begin at 11).
  - `columns_per_page` changes the page count: 1–100 with `rows_per_column=10` yields 5 pages at `columns_per_page=2` and 2 pages at `columns_per_page=5` (assert section count).
  - A POST without the differences checkbox omits `Differentia` from the response; a POST with it includes `Differentia`.
  - A non-htmx `POST /period` returns the complete page shell (doctype and page chrome), not a bare fragment.
  - `end - start + 1 > MAX_TABLE_ROWS` returns a visible error message, not a truncated table.
  - Malformed layout fields (`rows_per_column=abc`) and invalid values (`rows_per_column=9`, `columns_per_page=0`, `base=1`, `fractional_digits=0`) abort with 400.
- [ ] Run `python -m pytest tests/test_webapp.py -k period -q` and capture failure.
- [ ] Implement the routes.
- [ ] Run focused and full suites plus `git diff --check`.
- [ ] Commit `feat: serve period log tables in the browser` and report to `.superpowers/sdd/phase-08/task-5-report.md`.
