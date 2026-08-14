# Napier Tables

Integer-first logarithm table generation for configurable bases, precision, and input ranges.

The project is being built in layers. The current implementation includes the Python 3.14+ package foundation, validated table configuration, immutable table models, integer-only rounding/decimal formatting helpers, and a minimal Flask + SQLAlchemy website for storing table configurations. Logarithm series calculation, threaded generation, HTML output, local serving, Markdown, and PDF output are implemented incrementally according to the plans in [`docs/superpowers/plans`](docs/superpowers/plans/README.md).

## Requirements

- Python 3.14 or newer
- pytest for development and tests

## Development setup

From PowerShell:

```powershell
python -m pip install -e ".[test]"
python -m pytest -q
python -m compileall src tests
```

To run the website locally:

```powershell
.venv314\Scripts\python -m napier_tables --host 127.0.0.1 --port 5000
```

or, on macOS/Linux:

```bash
.venv314/bin/python -m napier_tables --host 127.0.0.1 --port 5000
```

The package uses a `src` layout. The test configuration adds `src` to pytest's import path while the package is developed locally.

## Design principles

- Table values use integer calculations; binary floating-point logarithms are not part of the calculation engine.
- Each input value is calculated independently so rounding cannot accumulate between rows.
- Python 3.14+ `ThreadPoolExecutor` will be used for independent table-generation work.
- HTML is the first served output, with modern and Napier-inspired presentation themes planned.
- The website uses htmx for partial updates and SQLAlchemy for sqlite-backed CRUD.
- Markdown and PDF are alternate renderings of the same immutable table data.

## Project plans

The implementation is organized by phase:

1. Foundation
2. Integer logarithm engine
3. Threaded generation
4. HTML output
5. Local web server
6. Markdown and PDF output

See the [design specification](docs/superpowers/specs/2026-08-12-logarithm-tables-design.md) and [layered implementation plan](docs/superpowers/plans/README.md).
