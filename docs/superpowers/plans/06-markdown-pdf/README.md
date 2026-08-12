# Phase 6: Markdown and PDF Outputs

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Every task is tests-first and ends with a focused test and commit.

**Goal:** Add Markdown and PDF renderings without duplicating calculation or table-generation logic.

**Architecture:** Markdown is a standard-library renderer. PDF is an optional adapter behind `PdfBackendError`; HTML and Markdown remain usable without the optional backend.

**Tech Stack:** Python 3.14+, standard-library Markdown generation, selected optional PDF backend, pytest.

## Global Constraints

- All formats consume the same immutable `LogTable`.
- Optional PDF installation must be explicit and documented.
- Cross-format tests compare row identity and formatted decimal text.

**Goal:** Add Markdown and PDF files as alternate renderings of the already-generated `LogTable`, without changing calculation or HTML behavior.

**Depends on:** Phase 5 stable HTML pipeline.

**Produces:** Markdown renderer, PDF renderer, output CLI options, cross-renderer tests.

**Files:** `src/napier_tables/render_markdown.py`, `src/napier_tables/render_pdf.py`, `src/napier_tables/cli.py`, `tests/test_render_markdown.py`, `tests/test_render_pdf.py`, `pyproject.toml`, `README.md`.

## Public symbols

- `render_markdown(table: LogTable, title: str | None = None) -> str`.
- `write_markdown(table: LogTable, output_path: Path, title: str | None = None) -> None`.
- `class PdfBackendError(RuntimeError)`.
- `write_pdf(table: LogTable, output_path: Path, theme: Theme = Theme.MODERN, title: str | None = None) -> None`.

The PDF backend must be an explicitly documented optional dependency. Importing `napier_tables` and using HTML/Markdown must work when it is absent. The selected backend and version must be pinned in project metadata or documented as an install extra before implementation.

## Tasks

### 6.1 Markdown renderer

Write failing tests requiring a title, configuration summary, Markdown table header, one row per input, escaped pipe characters, and exact decimal text. Implement `render_markdown()` using only `LogTable` and `scaled_to_text()`, then `write_markdown()` with the same UTF-8/newline policy as HTML. Run `python -m pytest tests/test_render_markdown.py -q`; commit `feat: render logarithm tables as Markdown`.

### 6.2 PDF backend boundary

Write failing tests that mock the selected PDF backend, assert the PDF writer receives the rendered table content and output path, and assert `PdfBackendError` when the optional dependency is unavailable. Implement a narrow adapter in `render_pdf.py`; do not duplicate logarithm or table-generation logic. Run `python -m pytest tests/test_render_pdf.py -q`; commit `feat: add optional PDF rendering boundary`.

### 6.3 PDF integration test

Add an environment-marked integration test that runs only when the PDF backend is installed. It must create a PDF, assert a non-zero file, verify the PDF header, and verify that the input values and title are extractable or otherwise present through the backend’s test API. Run `python -m pytest tests/test_render_pdf.py -q` with and without the optional extra; commit `test: verify optional PDF output`.

### 6.4 CLI output selection

Write failing tests for `--format html`, `--format markdown`, and `--format pdf`, including rejection of unsupported formats and required backend errors. Extend `cli.main()` to call the existing renderer boundary selected by a literal format enum or validated string. Run `python -m pytest tests/test_cli.py tests/test_render_html.py tests/test_render_markdown.py tests/test_render_pdf.py -q`; commit `feat: expose all table output formats`.

### 6.5 Final acceptance

Render one base-10, four-digit table in HTML, Markdown, and PDF. Compare row counts and decimal strings across all formats. Run `python -m pytest -q`, `python -m compileall src tests`, and `git diff --check`. Update `README.md` with optional PDF installation and limitations. Commit `docs: complete multi-format table workflow`.
