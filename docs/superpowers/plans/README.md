# Napier Tables Implementation Plans

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement one phase at a time. Do not skip phase handoffs.

**Goal:** Deliver integer-only, threaded logarithm tables through HTML first, then Markdown and PDF.

**Architecture:** Six ordered phases establish immutable contracts, exact calculation, threaded generation, renderers, serving, and optional PDF output. Each phase is independently testable.

**Tech Stack:** Python 3.14+, pytest, standard library, CSS, optional PDF backend isolated behind an adapter.

## Global Constraints

- Use tests-first red-green-refactor for every symbol.
- Use `ThreadPoolExecutor` for multi-worker generation.
- Keep output deterministic and calculation metadata private.
- Commit after each independently verified task and phase handoff.

> **For agentic workers:** Execute one phase at a time. Every task is tests-first: write the named failing test, run it, implement the smallest change, run the focused test, run the phase suite, and commit.

## Execution order

1. [01-foundation](01-foundation/README.md)
2. [02-integer-engine](02-integer-engine/README.md)
3. [03-threaded-generation](03-threaded-generation/README.md)
4. [04-html-output](04-html-output/README.md)
5. [05-local-server](05-local-server/README.md)
6. [06-markdown-pdf](06-markdown-pdf/README.md)
7. [07-historical-format](07-historical-format/README.md) — historical proportional log tables in the browser, N-resolution fixed decade + log precision

Each phase is independently testable. Do not start a later phase until its prerequisite handoff is committed and verified.
