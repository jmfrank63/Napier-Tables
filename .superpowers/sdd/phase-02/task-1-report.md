# Integer Engine Task 1 Report

## Status

Complete. Implemented only Task 1 integer rounding and decimal-text
formatting in the requested isolated worktree.

- Added `CalculationError` as the phase-local `ValueError` subtype used for
  invalid integer-engine inputs.
- Added `round_ratio(numerator, denominator, scale)` using integer
  multiplication, `divmod`, and remainder comparison only.
- Documented half-up behavior explicitly: exact halves round away from zero,
  including negative numerators.
- Added `scaled_to_text(scaled_value, fractional_digits)` using integer powers
  of ten and `divmod`, preserving trailing zeroes and leading fractional
  zeroes without floating point.
- Rejected non-positive denominators and scales, and negative fractional-digit
  precision.
- Added no logarithm series, bounds, range reduction, row calculation, binary
  floating point, `math.log`, or `decimal` code.
- Preserved the Phase 1 package exports: `TableConfig`, `ConfigurationError`,
  `LogRow`, and `LogTable`.

## Commit

Implementation commit: `5464fe763feecbb290229bb66c5090229c8970c9`

Message: `feat: add integer rounding and formatting`

The implementation commit contains both production code and the complete Task
1 test file.

## Tests

- Baseline before edits: `python -m pytest -q` passed, `16 passed in 0.07s`.
- Initial red phase: `python -m pytest tests/test_integer_log.py -k 'round or text' -q`
  failed during collection with the expected
  `ModuleNotFoundError: No module named 'napier_tables.integer_log'`.
- Behavioral red phase after adding callable stubs: the same focused command
  failed as expected, `12 failed in 0.20s`, because both helpers raised
  `NotImplementedError`.
- Focused green phase: the same focused command passed,
  `12 passed in 0.04s`.
- Full suite: `python -m pytest -q` passed, `28 passed in 0.09s`.
- Review: `git diff --check` passed with exit code 0.
- Staged review: `git diff --cached --check` passed before commit; both source
  and test files were included in the commit.

## Self-review

- Confirmed rounding uses no division operator or floating-point conversion;
  it compares twice the remainder with the positive denominator.
- Confirmed sign handling is symmetric and an exact negative half rounds away
  from zero.
- Confirmed decimal formatting handles zero precision, values below one,
  trailing zeroes, and negative values without producing a negative zero sign.
- Confirmed tests would catch changing `>=` to `>`, dropping negative sign
  handling, accepting non-positive denominator/scale values, losing fixed-width
  fractional padding, or accepting negative precision.
- Confirmed no files outside `src/napier_tables/integer_log.py`,
  `tests/test_integer_log.py`, and this required report were changed.

## Concerns

None. Tasks 2-5 remain intentionally unimplemented.

## Review Fix

Addressed the Phase 2 Task 1 review finding by importing the public
`CalculationError` from `napier_tables.integer_log` and asserting that exact
exception in every invalid-input test. Existing message assertions and all
behavioral coverage were preserved.

- Focused tests: `python -m pytest tests/test_integer_log.py -k 'round or text' -q`
- Full suite: `python -m pytest -q`
- Diff check: `git diff --check`
- Fix commit: `10756ce1ce0057ec670dc1980170ed70d7e24745` (report included in
  the amended commit)
