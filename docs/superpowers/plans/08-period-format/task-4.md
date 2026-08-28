# Period Format Task 4

Work only in the isolated implementation worktree. Read `08-period-format/README.md` first.

Implement the period HTML renderer in `src/napier_tables/period.py`.

Symbols: `render_period_html(table: PeriodTable, title: str | None = None) -> str`.

Rules: escaped title and cell text via `html.escape`; one `<section>` per `PeriodPage`; one `<table>` per `PeriodColumn` with `Numerus` / `Logarithmus` / `Differentia` heads (Differentia head and cells absent when differences are disabled); exact cell text from the builder; deterministic attribute ordering; byte-stable repeated renders; period stylesheet with a serif stack, ruled borders, and restrained ink-on-paper colors, no image assets. The renderer must not call the calculation engine.

- [ ] Write failing tests: a title containing `<b>` appears escaped; the fragment contains one section per page and one table per column; `Numerus`, `Logarithmus`, `Differentia` heads present (and `Differentia` absent when `show_differences=False`); a known cell's exact period-notation text appears verbatim; two renders of the same table are byte-identical.
- [ ] Run `python -m pytest tests/test_period.py -k render -q` and capture failure.
- [ ] Implement `render_period_html`.
- [ ] Run focused and full suites plus `git diff --check`.
- [ ] Commit `feat: render period log tables as HTML` and report to `.superpowers/sdd/phase-08/task-4-report.md`.
