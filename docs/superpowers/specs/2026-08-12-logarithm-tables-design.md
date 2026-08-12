# Napier Tables Design

## Goal

Build a Python repository that generates logarithm tables for configurable integer bases, input ranges, and decimal precision. HTML is the first output and is served through a local Python web server; Markdown and PDF are later renderings of the same generated table data.

## Scope

The first implementation milestone includes:

- A tests-first Python package for generating logarithm rows.
- Configurable integer base, fractional decimal digits, input start/end, and worker count.
- Independent integer-only calculation for every input value.
- Deterministic ordering regardless of worker count.
- HTML rendering with simple responsive CSS.
- A friendly modern style and a configurable Napier-inspired seventeenth-century style.
- A standard-library local web server for the generated HTML.

Markdown and PDF output are intentionally designed as follow-on renderers and are not required for the first implementation milestone.

## Mathematical contract

The public configuration is conceptually:

```python
TableConfig(
    base=10,
    fractional_digits=4,
    start=1,
    end=1000,
    workers=None,
)
```

The generator validates `base >= 2`, `fractional_digits >= 0`, `start >= 1`, and `end >= start`. A generated row represents the logarithm of one positive integer input in the requested base, rounded once to the requested number of fractional decimal digits.

The implementation must not use binary floating-point calculations for table values. It will use integer fixed-point arithmetic, range reduction, guard precision, and a final integer rounding step. Each input value is calculated independently; no rounded result is used as an input to another row. This prevents rounding error accumulation.

The internal algorithm must retain enough guard precision to make the final rounding decision exact for the implemented integer approximation. Its public output does not expose calculation metadata. Regenerating with more fractional digits is the supported way to obtain a more precise table.

The displayed logarithm format will initially be modern decimal notation. Historical rounding marks and characteristic-bar notation remain a documented extension point and must not be implied by the initial output until their convention is explicitly selected.

## Concurrency

The project targets Python 3.14 or newer and assumes the free-threaded Python build where applicable. It will use `concurrent.futures.ThreadPoolExecutor` to calculate independent input chunks concurrently. The implementation must not silently replace threading with a process pool or serial loop when multiple workers are requested.

Workers calculate disjoint input ranges. The coordinator reassembles rows by input value before rendering, making output deterministic for `workers=1`, `workers>1`, and the default worker setting. Worker count is configurable; `None` delegates the default sizing decision to Python’s executor.

Tests must compare serial and multithreaded results and verify that chunk boundaries do not alter table contents or ordering. Performance benchmarking is separate from correctness testing.

## Components

### Configuration and validation

Defines the immutable table configuration and validation errors. It owns no rendering or concurrency logic.

### Integer calculation

Provides small, testable integer helpers for fixed-point logarithm calculation and final rounding. The module exposes a single row-calculation boundary to the generator. It must document the scale, guard digits, range-reduction identity, and error bound used by the implementation.

### Table generation

Validates configuration, partitions the input range into deterministic chunks, dispatches chunks through `ThreadPoolExecutor`, calculates rows independently, and returns rows sorted by input value.

### Rendering

Converts ordered rows to HTML. Styles are selected by a named presentation theme. The modern theme is readable and responsive; the historical theme uses restrained typography, borders, spacing, and serif font stacks inspired by seventeenth-century printed mathematical tables without pretending to reproduce a specific typeface.

### Local serving

Generates or serves the HTML output directory using Python’s standard-library HTTP server. It supports selecting the output directory and port, and defaults to localhost. It does not require a web framework.

### Future renderers

Markdown and PDF renderers will consume the same ordered rows and table configuration. PDF generation will be added only after HTML output and its validation are stable.

## Data flow

```text
TableConfig
    -> validation
    -> deterministic input chunks
    -> ThreadPoolExecutor workers
    -> independently calculated integer-scaled rows
    -> ordered Table
    -> HTML renderer + theme CSS
    -> local standard-library web server
```

The table model contains only the input value and final rendered/logarithm value needed by output consumers. Intermediate remainders, guard values, and rounding decisions remain implementation details.

## Test-first requirements

No production implementation is written before its corresponding failing test. The implementation plan will use small red-green-refactor tasks.

Required tests include:

- configuration validation and immutable construction;
- integer helper behavior on exact identities and rounding boundaries;
- `log_base(1) == 0` and `log_base(base) == 1`;
- known reference values at multiple bases and precisions;
- rejection of unsupported or invalid inputs;
- serial versus multithreaded equality;
- deterministic ordering across chunk sizes and worker counts;
- HTML escaping, required table structure, selected theme classes, and stable CSS links;
- local server startup/response using an ephemeral port.

Reference-value tests may use independently prepared integer-scaled fixtures. They must not calculate expected values with the same production algorithm or binary floating point.

## Repository layout

```text
Napier-Tables/
├── src/napier_tables/
│   ├── config.py
│   ├── integer_log.py
│   ├── generate.py
│   ├── render_html.py
│   ├── themes.py
│   └── serve.py
├── tests/
├── configs/
├── web/
│   └── styles.css
├── docs/superpowers/specs/
├── docs/superpowers/plans/
├── pyproject.toml
├── README.md
└── .gitignore
```

The exact module split may be adjusted in the implementation plan only if the public boundaries and test coverage remain intact.

## Constraints and acceptance criteria

- Python 3.14+ is required.
- Table values use integer calculations only; no floating-point logarithm calls.
- Threading uses Python’s 3.14+ free-threaded capability where available.
- The same configuration produces byte-stable HTML for a fixed theme and renderer version.
- HTML is usable from a local web server without third-party runtime dependencies.
- A base-10, four-fractional-digit example is included.
- The repository begins with tests and implementation follows the tests-first workflow.
- The design is committed before the implementation plan is written.

## Deferred decisions

- The exact historical rounding marker convention.
- PDF backend and whether PDF generation requires an optional dependency.
- Whether the default table range should remain `1..1000` or be selected by a configuration file/CLI.
- Whether logarithm complements, interpolation tables, or characteristic/mantissa split tables are needed.
