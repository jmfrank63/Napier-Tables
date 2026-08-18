"""Integer arithmetic helpers for logarithm calculations."""

from fractions import Fraction

from .models import LogRow

_INITIAL_TERMS = 8
_MAX_TERMS = 1 << 20
_INITIAL_GUARD_DIGITS = 4
_MAX_GUARD_DIGITS = 1 << 10


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


def _floor(value: Fraction) -> int:
    """Return the greatest integer not above ``value`` using integer division."""
    return value.numerator // value.denominator


def _ceil(value: Fraction) -> int:
    """Return the least integer not below ``value`` using integer division."""
    return -((-value.numerator) // value.denominator)


def _ln_bounds(value: int, scale: int) -> tuple[int, int]:
    """Bound ``ln(value) * scale`` by integers that differ by at most one.

    Series terms double until the bounds meet at ``scale``, so the caller
    receives a converged interval rather than a truncated series value.
    """
    if value < 1:
        raise CalculationError("value must be at least 1")
    if scale <= 0:
        raise CalculationError("scale must be positive")
    if value == 1:
        return 0, 0

    numerator, denominator, exponent = _reduce_ratio(value, 1)
    atanh_numerator = numerator - denominator
    atanh_denominator = numerator + denominator

    terms = _INITIAL_TERMS
    while terms <= _MAX_TERMS:
        lower, upper = _atanh_bounds(atanh_numerator, atanh_denominator, terms)
        ln2_lower, ln2_upper = _atanh_bounds(1, 3, terms)

        # A negative exponent flips which ln(2) bound is the conservative one.
        if exponent >= 0:
            total_lower = 2 * lower + 2 * ln2_lower * exponent
            total_upper = 2 * upper + 2 * ln2_upper * exponent
        else:
            total_lower = 2 * lower + 2 * ln2_upper * exponent
            total_upper = 2 * upper + 2 * ln2_lower * exponent

        scaled_lower = _floor(total_lower * scale)
        scaled_upper = _ceil(total_upper * scale)
        if scaled_upper - scaled_lower <= 1:
            return scaled_lower, scaled_upper

        terms *= 2

    raise CalculationError("logarithm bounds did not converge")


def _ratio_bounds(value: int, base: int, scale: int) -> tuple[int, int]:
    """Bound ``log(value, base) * scale`` by integer cross-multiplication."""
    if value < 1:
        raise CalculationError("value must be at least 1")
    if base < 2:
        raise CalculationError("base must be at least 2")
    if scale <= 0:
        raise CalculationError("scale must be positive")
    if value == 1:
        return 0, 0

    guard = scale * 10**_INITIAL_GUARD_DIGITS
    value_lower, value_upper = _ln_bounds(value, guard)
    base_lower, base_upper = _ln_bounds(base, guard)
    if base_lower <= 0:
        raise CalculationError("base logarithm bounds did not converge")

    lower = (value_lower * scale) // base_upper
    upper = -((-(value_upper * scale)) // base_lower)
    return lower, upper


def calculate_log_scaled(value: int, base: int, scale: int) -> int:
    """Return ``log(value, base) * scale`` rounded once, using integers only.

    Guard digits double until the lower and upper bounds round to the same
    scaled integer, so rounding happens once on a converged interval.
    """
    if value < 1:
        raise CalculationError("value must be at least 1")
    if base < 2:
        raise CalculationError("base must be at least 2")
    if scale <= 0:
        raise CalculationError("scale must be positive")
    if value == 1:
        return 0

    guard_digits = _INITIAL_GUARD_DIGITS
    while guard_digits <= _MAX_GUARD_DIGITS:
        factor = 10**guard_digits
        lower, upper = _ratio_bounds(value, base, scale * factor)
        rounded_lower = round_ratio(lower, factor, 1)
        rounded_upper = round_ratio(upper, factor, 1)
        if rounded_lower == rounded_upper:
            return rounded_lower

        guard_digits *= 2

    raise CalculationError("logarithm result did not converge")


def calculate_row(value: int, base: int, fractional_digits: int) -> LogRow:
    """Calculate one independent logarithm row at the requested precision."""
    if fractional_digits < 0:
        raise CalculationError("fractional_digits must be non-negative")

    scaled_value = calculate_log_scaled(value, base, 10**fractional_digits)
    return LogRow(
        input_value=value,
        scaled_value=scaled_value,
        fractional_digits=fractional_digits,
    )
