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
