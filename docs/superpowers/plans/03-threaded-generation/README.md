# Phase 3: Threaded Generation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Every task is tests-first and ends with a focused test and commit.

**Goal:** Generate deterministic tables through Python 3.14+ threads.

**Architecture:** Pure row workers process disjoint ranges; the coordinator collects and sorts immutable rows before constructing `LogTable`.

**Tech Stack:** Python 3.14+, `concurrent.futures.ThreadPoolExecutor`, pytest, argparse.

## Global Constraints

- Multiple workers must use `ThreadPoolExecutor`, never a process pool.
- Serial and threaded results must be exactly equal.
- Worker completion order must never determine output order.

**Goal:** Generate deterministic ordered tables with Python 3.14+ `ThreadPoolExecutor`, including free-threaded builds.

**Depends on:** Phase 1 models and Phase 2 `calculate_row`.

**Produces:** `generate.py`, serial/multithreaded generation, CLI generation entry point.

**Files:** `src/napier_tables/generate.py`, `src/napier_tables/cli.py`, `tests/test_generate.py`, `tests/test_cli.py`.

## Public symbols

- `chunk_range(start: int, end: int, chunks: int) -> tuple[range, ...]`.
- `generate_table(config: TableConfig) -> LogTable`.
- `generate_chunk(values: range, base: int, fractional_digits: int) -> tuple[LogRow, ...]`.
- `main(argv: Sequence[str] | None = None) -> int`.

## Tasks

### 3.1 Deterministic chunking

Write failing tests for empty/one-item ranges, more chunks than values, balanced contiguous chunks, no overlap, and complete coverage. Implement `chunk_range()` with integer division and no randomization. Run `python -m pytest tests/test_generate.py -k chunk -q`; commit `feat: add deterministic input chunking`.

### 3.2 Chunk worker

Write failing tests that monkeypatch `napier_tables.generate.calculate_row` and assert `generate_chunk(range(2, 5), 10, 4)` calls each input once and returns input order. Implement `generate_chunk()` as a pure worker with no shared mutable state. Run `python -m pytest tests/test_generate.py -k chunk_worker -q`; commit `feat: add independent generation worker`.

### 3.3 Serial coordinator

Write failing tests for `generate_table(TableConfig(..., workers=1))`, empty-invalid ranges, and row/config consistency. Implement `generate_table()` using `config.validate()`, `chunk_range()`, and one `generate_chunk()` call when workers is 1. Run `python -m pytest tests/test_generate.py -k serial -q`; commit `feat: generate ordered serial tables`.

### 3.4 ThreadPoolExecutor coordinator

Write failing tests comparing workers `1`, `2`, and `8`, asserting exact row equality and sorted values. Add an executor spy test asserting `ThreadPoolExecutor` is constructed when `workers > 1`; assert no `ProcessPoolExecutor` is used. Implement the threaded branch with `concurrent.futures.ThreadPoolExecutor(max_workers=config.workers)`, submit one future per chunk, collect all results, and sort rows by `input_value` before constructing `LogTable`. Run `python -m pytest tests/test_generate.py -k threaded -q`; commit `feat: generate tables with Python threads`.

### 3.5 CLI boundary

Write failing tests for `main(["--base", "10", "--digits", "4", "--start", "1", "--end", "3"])`, invalid arguments returning exit code 2, and an output path being created only by the later renderer integration. Implement `cli.main()` with `argparse`, configuration construction, and a temporary textual summary; do not add HTML logic here. Run `python -m pytest tests/test_cli.py -q`; commit `feat: add generation CLI contract`.

### 3.6 Threaded handoff

Run `python -m pytest -q`. Record the supported interpreter command `python --version` and require Python 3.14+. Handoff: Phase 4 consumes `generate_table()` and receives stable row ordering; rendering must not recalculate logarithms. Commit `docs: record threaded generation handoff`.
