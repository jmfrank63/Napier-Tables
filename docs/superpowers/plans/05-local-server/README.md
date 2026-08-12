# Phase 5: Local Web Server

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Every task is tests-first and ends with a focused test and commit.

**Goal:** Serve generated HTML safely through a local standard-library server.

**Architecture:** A server handle owns a `ThreadingHTTPServer` and daemon thread; the generator/writer composition is tested separately from HTTP lifecycle.

**Tech Stack:** Python 3.14+, `http.server`, `threading`, `urllib`, pytest.

## Global Constraints

- Default bind host is `127.0.0.1`.
- Port `0` is supported for tests and returns the selected ephemeral port.
- `close()` must shut down the server and join its thread.

**Goal:** Generate and serve the HTML table through a local standard-library web server.

**Depends on:** Phase 4 HTML writer.

**Produces:** `serve.py`, server CLI options, local HTTP tests.

**Files:** `src/napier_tables/serve.py`, `src/napier_tables/cli.py`, `tests/test_serve.py`, `README.md`.

## Public symbols

- `class ServerHandle`: `host: str`, `port: int`, `thread: Thread`, `close() -> None`.
- `serve_directory(directory: Path, host: str = "127.0.0.1", port: int = 0) -> ServerHandle`.
- `serve_generated_table(table: LogTable, output_path: Path, theme: Theme = Theme.MODERN, host: str = "127.0.0.1", port: int = 0) -> ServerHandle`.

## Tasks

### 5.1 Directory server

Write failing tests that create a temporary `index.html`, call `serve_directory(..., port=0)`, fetch it with `urllib.request.urlopen`, assert HTTP 200 and exact bytes, then call `close()` and assert the thread exits. Implement a `ThreadingHTTPServer` wrapper using `SimpleHTTPRequestHandler` bound to the requested directory and a daemon serving thread. Run `python -m pytest tests/test_serve.py -k directory -q`; commit `feat: serve generated files locally`.

### 5.2 Generated-table server

Write failing tests for `serve_generated_table()` writing HTML before serving, returning an ephemeral port, and exposing the selected theme. Implement the composition of `write_html()` and `serve_directory()`. Run `python -m pytest tests/test_serve.py -k generated -q`; commit `feat: serve generated HTML tables`.

### 5.3 CLI integration

Write failing tests for `main(["serve", "--base", "10", "--digits", "4", "--start", "1", "--end", "3", "--port", "0"])` parser behavior and a non-blocking test-mode server helper. Extend the CLI with explicit `generate` and `serve` subcommands; keep long-running serving in the command path and keep unit tests on `serve_generated_table()`. Run `python -m pytest tests/test_cli.py tests/test_serve.py -q`; commit `feat: add local serve command`.

### 5.4 Documentation and acceptance

Update `README.md` with exact PowerShell commands for installation, test execution, HTML generation, and local serving. Run `python -m pytest -q`, `python -m compileall src tests`, and a manual `python -m napier_tables serve --base 10 --digits 4 --start 1 --end 20`. Commit `docs: document local HTML workflow`.
