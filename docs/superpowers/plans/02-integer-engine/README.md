# Phase 2: Integer Logarithm Engine

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Every task is tests-first and ends with a focused test and commit.

**Goal:** Produce independently calculated, correctly rounded logarithm rows using integer/rational arithmetic.

**Architecture:** Exact rational range reduction and bounded atanh series feed a fixed-point ratio calculation. The public boundary returns only a `LogRow`.

**Tech Stack:** Python 3.14+, pytest, standard-library `fractions.Fraction` only as an exact rational container.

## Global Constraints

- No binary floating point, `math.log`, `decimal`, or accumulated row state.
- Final rounding occurs once after convergence of lower and upper bounds.
- Every public symbol has an independent reference or boundary test.

**Goal:** Calculate each logarithm using integer/rational arithmetic, guard precision, and one final rounding operation.

**Depends on:** Phase 1 models.

**Produces:** `integer_log.py` with independently testable exact helpers and `calculate_row()`.

**Files:** `src/napier_tables/integer_log.py`, `tests/test_integer_log.py`, `tests/fixtures/reference_values.py`.

## Mathematical invariants

Use rational atanh series with range reduction. For positive rational `p/q`, reduce by powers of two until the ratio is in `[1, 2)`, then use `z=(p-q)/(p+q)`, where `0 <= z <= 1/3`, and `ln(p/q)=2*(z+z**3/3+...)` plus/subtract the exact `ln(2)` series generated with `z=1/3`. Maintain lower/upper rational bounds; stop only when both bounds round to the same requested scaled integer. Compute `ln(value)/ln(base)` by integer cross-multiplication of those bounds. No `float`, `math.log`, `decimal`, or prior row result is allowed.

## Public symbols

- `class CalculationError(ValueError)`.
- `round_ratio(numerator: int, denominator: int, scale: int) -> int`.
- `scaled_to_text(scaled_value: int, fractional_digits: int) -> str`.
- `calculate_log_scaled(value: int, base: int, scale: int) -> int`.
- `calculate_row(value: int, base: int, fractional_digits: int) -> LogRow`.

Private helpers must have explicit type hints and tests at their owning task; likely helpers include `_reduce_ratio`, `_atanh_bounds`, `_ln_bounds`, and `_ratio_bounds`.

## Tasks

### 2.1 Integer rounding and formatting

Write failing tests for `round_ratio(1, 3, 10000) == 3333`, exact halves using the chosen half-up rule, negative numerator behavior, denominator zero, and `scaled_to_text(3010, 4) == "0.3010"` plus values requiring a leading zero.

Implement `round_ratio(numerator: int, denominator: int, scale: int) -> int` with positive denominator validation and integer quotient/remainder logic. Implement `scaled_to_text(scaled_value: int, fractional_digits: int) -> str` without floating point. Run `python -m pytest tests/test_integer_log.py -k 'round or text' -q`; commit `feat: add integer rounding and formatting`.

### 2.2 Range reduction and atanh bounds

Write failing tests for `_reduce_ratio(1, 1)`, ratios exactly at 2, reciprocal ratios, and the invariant that the reduced ratio lies in `[1, 2)`. Add independent fixture checks for the first terms of `ln(2)` and `ln(3/2)`.

Implement `_reduce_ratio(numerator: int, denominator: int) -> tuple[int, int, int]`, returning normalized numerator, denominator, and signed power-of-two exponent. Implement `_atanh_bounds(numerator: int, denominator: int, terms: int) -> tuple[Fraction, Fraction]` using integer numerator/denominator arithmetic; `Fraction` is permitted as an exact rational container, but not as a floating-point approximation. Run `python -m pytest tests/test_integer_log.py -k 'reduce or atanh' -q`; commit `feat: add bounded integer range reduction`.

### 2.3 Logarithm bounds and scaled result

Write failing tests for `calculate_log_scaled(1, 10, 10000) == 0`, `calculate_log_scaled(10, 10, 10000) == 10000`, base 2 values, and independently prepared reference fixtures for base 10 values `2`, `3`, and `100` at four fractional digits.

Implement `_ln_bounds(value: int, scale: int) -> tuple[int, int]` and `_ratio_bounds(value: int, base: int, scale: int) -> tuple[int, int]`. Each returns integer lower/upper bounds at guard scale and increases series terms until both bounds produce the same final rounded result. Implement `calculate_log_scaled(value: int, base: int, scale: int) -> int`, validating `value >= 1`, `base >= 2`, and positive scale. Run `python -m pytest tests/test_integer_log.py -k 'log_scaled or identity or reference' -q`; commit `feat: calculate integer logarithms with bounded rounding`.

### 2.4 Row boundary

Write failing tests for `calculate_row(3, 10, 4)` and invalid values. Implement `calculate_row(value: int, base: int, fractional_digits: int) -> LogRow` by deriving `scale=10**fractional_digits`, calling `calculate_log_scaled`, and constructing the Phase 1 model. Run `python -m pytest tests/test_integer_log.py -q`; commit `feat: expose logarithm row calculation`.

### 2.5 Engine handoff

Run `python -m pytest -q`, verify no production module imports `math.log` or performs floating-point table calculations, and document the bound-convergence invariant in the phase README. Handoff: Phase 3 may call only `calculate_row()` for table rows and may not share mutable calculation state. Commit `docs: record integer engine handoff`.
