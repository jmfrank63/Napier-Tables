---
name: superpowers
description: "Use when working in Napier Tables on the layered logarithm-table plan under docs/superpowers/plans, especially phase-by-phase implementation, tests-first red-green-refactor, integer-only logarithm generation, threaded generation, HTML rendering, serving, and later Markdown/PDF output."
argument-hint: Phase, task, or file to work on
disable-model-invocation: true
---

# Superpowers Workflow

Use this skill for the Napier Tables implementation plan.

## Core rules

- Treat [docs/superpowers/plans/README.md](docs/superpowers/plans/README.md) and the phase README for the current phase as the source of truth.
- Work one phase at a time and do not skip phase handoffs.
- Start from the smallest concrete anchor: a failing test, a nearby file, a symbol, or the current phase task.
- Before the first edit, identify one local hypothesis and one cheap check that could disconfirm it.
- Use tests-first red-green-refactor for every public symbol or behavior change.
- Keep table generation deterministic, integer-only, and independent per input value.
- Prefer linking to existing docs instead of repeating them.

## Execution loop

1. Read the relevant phase docs and nearby implementation.
2. Write the named failing test first.
3. Make the smallest change that can satisfy that test.
4. Run the focused test immediately.
5. If it passes, run the narrow phase or module test set.
6. Stop at the phase boundary until the handoff is verified.

## Working style

- Use the `Explore` subagent when you need quick workspace reconnaissance.
- Keep edits small and reversible.
- Prefer standard-library solutions unless the phase docs require otherwise.
- Preserve stable ordering and public contracts across workers, renderers, and servers.

## Useful references

- [Design spec](docs/superpowers/specs/2026-08-12-logarithm-tables-design.md)
- [Implementation plans](docs/superpowers/plans/README.md)
