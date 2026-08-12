# Foundation Task 2

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Work only in `C:/Users/jmfrank/source/repos/jmfrank63/Napier-Tables/.worktrees/implement-logarithm-tables`.

**Goal:** Add the immutable configuration contract.

**Files:** Create `src/napier_tables/config.py`, modify `src/napier_tables/__init__.py`, and create/extend `tests/test_config.py`.

**Symbols:** `ConfigurationError(ValueError)` and frozen slotted `TableConfig` with fields `base: int = 10`, `fractional_digits: int = 4`, `start: int = 1`, `end: int = 1000`, `workers: int | None = None`; method `validate(self) -> None`.

- [ ] Write tests for valid construction, frozen assignment failure, and each invalid field.
- [ ] Run `python -m pytest tests/test_config.py -q`; confirm the new behavior fails before implementation.
- [ ] Implement `ConfigurationError`, `TableConfig`, and `validate()` with field-specific messages.
- [ ] Re-export the two symbols from `napier_tables`.
- [ ] Run `python -m pytest tests/test_config.py -q` and `python -m pytest -q`.
- [ ] Commit with message `feat: add validated table configuration`.

**Report:** Write implementation status, commit hash, tests, and concerns to `.superpowers/sdd/phase-01/task-2-report.md`.
