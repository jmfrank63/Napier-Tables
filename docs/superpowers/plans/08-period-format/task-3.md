# Period Format Task 3

Work only in the isolated implementation worktree. Read `08-period-format/README.md` first.

Implement the folio layout builder in `src/napier_tables/period.py`.

Symbols: `class PeriodConfig` (`@dataclass(frozen=True, slots=True, kw_only=True)` — `base` has a default and precedes the required fields, so the dataclass must be keyword-only or it will not compile) with `base: int = 10`, `fractional_digits: int` (≥ 1), `start: int` (≥ 1), `end: int` (≥ `start`), `rows_per_column: int = 50` (≥ 10), `columns_per_page: int = 3` (≥ 1), `show_differences: bool = True`, and `validate() -> None`; `class PeriodCell` (`numerus: str`, `logarithmus: str`, `differentia: str | None`); `class PeriodColumn` (`cells: tuple[PeriodCell, ...]`); `class PeriodPage` (`columns: tuple[PeriodColumn, ...]`); `class PeriodTable` (`config: PeriodConfig`, `pages: tuple[PeriodPage, ...]`); `build_period_table(config: PeriodConfig) -> PeriodTable`.

Layout rules: values fill column-major — down each column (`rows_per_column` values), then the next column group, then the next page, as the printed chiliads were set. Each `differentia` is `difference_text` against the **next** value's scaled logarithm, including across column and page boundaries; the final value of the whole table shows an em dash (—). `show_differences=False` sets every `differentia` to `None`. All logarithms come from one `generate_table` call; differences are integer subtractions of final scaled values, never re-rounded.

- [ ] Write failing tests: `PeriodConfig(fractional_digits=4, start=1, end=1000)` builds 7 pages (150 values per page, last partial); page 1 column 1 holds 1–50 and column 2 holds 51–100; a boundary differentia (value 50 vs 51, value 150 vs 151) matches `difference_text` of the adjacent scaled values; the last cell's differentia is `"—"`; `show_differences=False` yields `differentia is None`; invalid configs (`rows_per_column=9`, `columns_per_page=0`, `fractional_digits=0`) raise.
- [ ] Run `python -m pytest tests/test_period.py -k build -q` and capture failure.
- [ ] Implement the dataclasses and `build_period_table`.
- [ ] Run focused and full suites plus `git diff --check`.
- [ ] Commit `feat: build period folio table layout` and report to `.superpowers/sdd/phase-08/task-3-report.md`.
