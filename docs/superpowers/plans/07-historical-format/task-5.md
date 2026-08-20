# Historical Format Task 5

Work only in the isolated implementation worktree. Read `07-historical-format/README.md` first.

Phase handoff: verify the whole suite and a representative browser render.

- [ ] Run `python -m pytest -q` and confirm green.
- [ ] Run `git diff --check`.
- [ ] Manually verify a base-10, resolution-1 (10–100), 4-fractional-digit historical table renders through `POST /historical` (or `GET /historical` form) in the browser; confirm 100 is excluded and no interpolation table is shown.
- [ ] Commit `docs: record historical format handoff` and report to `.superpowers/sdd/phase-07/task-5-report.md`.