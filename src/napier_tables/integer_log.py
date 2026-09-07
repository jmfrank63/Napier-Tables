"""Integer arithmetic helpers for logarithm calculations."""

from fractions import Fraction


class CalculationError(ValueError):
    """Raised when an integer logarithm calculation input is invalid."""


def round_ratio(numerator: int, denominator: int, scale: int) -> int:
    """Round ``numerator / denominator`` at ``scale`` using half-up.

    Exact halves round away from zero, so the rule is symmetric for negative
    numerators. The calculation uses only integer quotient and remainder
    arithmetic.
    """
    if denominator <= 0:
        raise CalculationError("denominator must be positive")
    if scale <= 0:
        raise CalculationError("scale must be positive")

    quotient, remainder = divmod(abs(numerator) * scale, denominator)
    if remainder * 2 >= denominator:
        quotient += 1

    return -quotient if numerator < 0 else quotient


def scaled_to_text(scaled_value: int, fractional_digits: int) -> str:
    """Format a scaled integer as decimal text without floating point."""
    if fractional_digits < 0:
        raise CalculationError("fractional_digits must be non-negative")
    if fractional_digits == 0:
        return str(scaled_value)

    scale = 10**fractional_digits
    whole, fractional = divmod(abs(scaled_value), scale)
    sign = "-" if scaled_value < 0 else ""
    return f"{sign}{whole}.{fractional:0{fractional_digits}d}"


def _reduce_ratio(numerator: int, denominator: int) -> tuple[int, int, int]:
    """Normalize a positive ratio to ``[1, 2)`` using powers of two."""
    if numerator <= 0:
        raise CalculationError("numerator must be positive")
    if denominator <= 0:
        raise CalculationError("denominator must be positive")

    exponent = 0
    while numerator < denominator:
        numerator *= 2
        exponent -= 1
    while numerator >= 2 * denominator:
        denominator *= 2
        exponent += 1

    reduced = Fraction(numerator, denominator)
    return reduced.numerator, reduced.denominator, exponent


def _ln_fraction(numerator: int, denominator: int, terms: int) -> Fraction:
    """Approximate ``ln(numerator / denominator)`` as an exact rational midpoint."""
    if numerator <= 0:
        raise CalculationError("numerator must be positive")
    if denominator <= 0:
        raise CalculationError("denominator must be positive")

    reduced_numerator, reduced_denominator, exponent = _reduce_ratio(
        numerator, denominator
    )
    lower, upper = _atanh_bounds(
        reduced_numerator - reduced_denominator,
        reduced_numerator + reduced_denominator,
        terms,
    )
    ln_value = lower + upper
    if exponent:
        ln_two_lower, ln_two_upper = _atanh_bounds(1, 3, terms)
        ln_value += exponent * (ln_two_lower + ln_two_upper)
    return ln_value


def log10_scaled(
    scaled_value: int, value_digits: int, fractional_digits: int
) -> int:
    """Round ``log10(scaled_value / 10**value_digits)`` at ``10**fractional_digits``.

    The input is a scaled positive value such as ``123`` with ``value_digits``
    equal to ``2``, meaning ``1.23``. The result uses the exact atanh series
    with rational midpoints and half-up rounding, never floating point.
    """
    if value_digits < 0:
        raise CalculationError("value_digits must be non-negative")
    if scaled_value <= 0:
        raise CalculationError("scaled_value must be positive")

    terms = fractional_digits + 16
    ln_value = _ln_fraction(scaled_value, 10**value_digits, terms)
    ln_ten = _ln_fraction(10, 1, terms)
    ratio = ln_value / ln_ten
    return round_ratio(ratio.numerator, ratio.denominator, 10**fractional_digits)


def _atanh_bounds(
    numerator: int, denominator: int, terms: int
) -> tuple[Fraction, Fraction]:
    """Bound ``atanh(numerator / denominator)`` by exact rationals."""
    if denominator <= 0:
        raise CalculationError("denominator must be positive")
    if numerator < 0 or numerator >= denominator:
        raise CalculationError("atanh ratio must be in [0, 1)")
    if terms <= 0:
        raise CalculationError("terms must be positive")

    ratio = Fraction(numerator, denominator)
    ratio_squared = ratio * ratio
    power = ratio
    lower = Fraction(0)

    for index in range(terms):
        lower += power / (2 * index + 1)
        power *= ratio_squared

    tail_upper = power / ((2 * terms + 1) * (1 - ratio_squared))
    return lower, lower + tail_upper
