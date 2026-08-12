# Phase 1: Foundation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Every task is tests-first and ends with a focused test and commit.

**Goal:** Create the package foundation and immutable table contracts.

**Architecture:** A `src`-layout package separates configuration from immutable data models. No calculation, rendering, or concurrency is introduced in this phase.

**Tech Stack:** Python 3.14+, pytest, standard library dataclasses, argparse-compatible packaging.

## Global Constraints

- Python `>=3.14`.
- Tests must be written and shown failing before implementation.
- Public models are frozen and slot-based.
- No third-party runtime dependency.

**Goal:** Create the Python 3.14+ package, test harness, public data model, and CLI conventions without implementing logarithm mathematics.

**Depends on:** none.

**Produces:** importable `napier_tables` package; immutable `TableConfig`; ordered `LogRow`/`LogTable` models; project test commands.

**Files:** `pyproject.toml`, `README.md`, `.gitignore`, `src/napier_tables/__init__.py`, `src/napier_tables/config.py`, `src/napier_tables/models.py`, `tests/test_config.py`, `tests/test_models.py`.

## Public symbols

- `config.py`: `class ConfigurationError(ValueError)`, `class TableConfig`, `TableConfig.validate() -> None`.
- `models.py`: `class LogRow`, `class LogTable`, `LogTable.values() -> tuple[int, ...]`.
- `__init__.py`: re-export `TableConfig`, `ConfigurationError`, `LogRow`, and `LogTable`.

## Phase 1 handoff

Foundation verification completed on implementation commit `7e9932f083c0cea1553ae1107608f7f3255c444b`:

- `python -m pytest -q` — 16 passed in 0.06s.
- `python -m compileall src tests` — completed successfully.
- `PYTHONPATH=src python -c "from napier_tables import ConfigurationError, LogRow, LogTable, TableConfig; print('exports confirmed')"` — exports confirmed.

Phase 2 may construct `TableConfig`, `LogRow`, and `LogTable` through these public imports. These frozen, slot-based models must not be mutated; Phase 2 must preserve the validated configuration and ordered immutable rows when producing logarithm tables.

## Tasks

### 1.1 Project metadata and failing import test

Create `pyproject.toml` requiring Python `>=3.14`, a `src` layout, `pytest` as the test dependency, and `napier-table` as the console-script name reserved for later phases. Create `.gitignore` for Python caches, virtual environments, generated HTML/PDF, and build output.

Write `tests/test_config.py::test_package_imports_and_python_requirement_metadata` and run `python -m pytest tests/test_config.py::test_package_imports_and_python_requirement_metadata -q`; it must fail because the package does not exist. Add the minimal package and metadata, rerun, and commit `build: establish Python package foundation`.

### 1.2 Configuration symbol

Write failing tests for `TableConfig(base=10, fractional_digits=4, start=1, end=1000, workers=None)`, frozen assignment failure, and `validate()` rejection of base `< 2`, negative precision, start `< 1`, end `< start`, and workers `< 1`.

Implement:

```python
@dataclass(frozen=True, slots=True)
class TableConfig:
    base: int = 10
    fractional_digits: int = 4
    start: int = 1
    end: int = 1000
    workers: int | None = None
    def validate(self) -> None: ...
```

`validate()` returns `None` for valid values and raises `ConfigurationError` with a field-specific message. Run `python -m pytest tests/test_config.py -q`; commit `feat: add validated table configuration`.

### 1.3 Ordered model symbols

Write failing tests for:

```python
@dataclass(frozen=True, slots=True)
class LogRow:
    input_value: int
    scaled_value: int
    fractional_digits: int
```

and:

```python
@dataclass(frozen=True, slots=True)
class LogTable:
    config: TableConfig
    rows: tuple[LogRow, ...]
    def values(self) -> tuple[int, ...]: ...
```

Reject non-positive row inputs, mismatched precision, duplicate inputs, and rows not strictly increasing. `values()` returns input values only. Run `python -m pytest tests/test_models.py -q`; commit `feat: add immutable table models`.

### 1.4 Foundation handoff

Run `python -m pytest -q` and `python -m compileall src tests`. Confirm imports expose exactly the symbols named above. Update `01-foundation/README.md` with the commit hash and handoff: later phases may construct `TableConfig`, `LogRow`, and `LogTable`, but must not mutate them. Commit `docs: record foundation handoff`.
