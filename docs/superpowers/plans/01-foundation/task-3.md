# Foundation Task 3

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Work only in `C:/Users/jmfrank/source/repos/jmfrank63/Napier-Tables/.worktrees/implement-logarithm-tables`.

**Goal:** Add immutable ordered table models.

**Files:** Create `src/napier_tables/models.py`, modify `src/napier_tables/__init__.py`, and create `tests/test_models.py`.

**Symbols:** frozen slotted `LogRow(input_value: int, scaled_value: int, fractional_digits: int)` and frozen slotted `LogTable(config: TableConfig, rows: tuple[LogRow, ...])`; method `LogTable.values(self) -> tuple[int, ...]`.

- [ ] Write tests for valid rows/table, `values()`, frozen assignment, non-positive inputs, precision mismatch, duplicate inputs, and non-increasing rows.
- [ ] Run `python -m pytest tests/test_models.py -q`; confirm failure before implementation.
- [ ] Implement model validation and the `values()` method.
- [ ] Re-export both models.
- [ ] Run `python -m pytest tests/test_models.py -q` and `python -m pytest -q`.
- [ ] Commit with message `feat: add immutable table models`.

**Report:** Write implementation status, commit hash, tests, and concerns to `.superpowers/sdd/phase-01/task-3-report.md`.
