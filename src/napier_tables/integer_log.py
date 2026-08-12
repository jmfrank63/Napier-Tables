"""Integer arithmetic helpers for logarithm calculations."""


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
