# Foundation Task 1

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Work only in `C:/Users/jmfrank/source/repos/jmfrank63/Napier-Tables/.worktrees/implement-logarithm-tables`.

**Goal:** Establish the Python package and test harness.

**Files:** Create `pyproject.toml`, `.gitignore` additions only if needed, `src/napier_tables/__init__.py`, and `tests/test_config.py`.

**Requirements:** Python `>=3.14`; `src` layout; pytest test dependency; package import must work. Do not implement configuration or logarithm behavior yet.

- [ ] Write `tests/test_config.py::test_package_imports_and_python_requirement_metadata` and assert the package imports and metadata declares Python 3.14 or newer.
- [ ] Run `python -m pytest tests/test_config.py::test_package_imports_and_python_requirement_metadata -q`; confirm it fails because the package is absent.
- [ ] Add the minimal package metadata and empty importable package.
- [ ] Run the focused test and then `python -m pytest -q`.
- [ ] Commit with message `build: establish Python package foundation`.

**Report:** Write implementation status, commit hash, tests, and concerns to `.superpowers/sdd/phase-01/task-1-report.md`.
