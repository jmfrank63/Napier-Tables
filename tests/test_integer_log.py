import math

from fractions import Fraction

import pytest

from napier_tables import integer_log
from napier_tables.integer_log import (
    CalculationError,
    log10_scaled,
    round_ratio,
    scaled_to_text,
)


def test_round_ratio_rounds_thirds_to_nearest_scaled_integer():
    assert round_ratio(1, 3, 10_000) == 3_333
    assert round_ratio(2, 3, 10_000) == 6_667


def test_round_ratio_rounds_exact_halves_away_from_zero():
    assert round_ratio(1, 2, 1) == 1
    assert round_ratio(-1, 2, 1) == -1


def test_round_ratio_handles_negative_numerators_symmetrically():
    assert round_ratio(-1, 3, 10_000) == -3_333
    assert round_ratio(-2, 3, 10_000) == -6_667


@pytest.mark.parametrize("denominator", [0, -1])
def test_round_ratio_rejects_non_positive_denominator(denominator):
    with pytest.raises(CalculationError, match="^denominator must be positive$"):
        round_ratio(1, denominator, 10_000)


@pytest.mark.parametrize("scale", [0, -1])
def test_round_ratio_rejects_non_positive_scale(scale):
    with pytest.raises(CalculationError, match="^scale must be positive$"):
        round_ratio(1, 3, scale)


def test_scaled_to_text_preserves_requested_fractional_digits():
    assert scaled_to_text(3_010, 4) == "0.3010"


def test_scaled_to_text_pads_values_requiring_leading_zeroes():
    assert scaled_to_text(1, 4) == "0.0001"


def test_scaled_to_text_formats_negative_values_without_floating_point():
    assert scaled_to_text(-3_010, 4) == "-0.3010"
    assert scaled_to_text(-1, 4) == "-0.0001"


def test_scaled_to_text_supports_zero_fractional_digits():
    assert scaled_to_text(3_010, 0) == "3010"


def test_scaled_to_text_rejects_negative_fractional_digits():
    with pytest.raises(
        CalculationError, match="^fractional_digits must be non-negative$"
    ):
        scaled_to_text(3_010, -1)


def test_reduce_ratio_leaves_unity_normalized():
    assert integer_log._reduce_ratio(1, 1) == (1, 1, 0)


@pytest.mark.parametrize(
    ("numerator", "denominator", "expected"),
    [
        (2, 1, (1, 1, 1)),
        (8, 1, (1, 1, 3)),
        (1, 2, (1, 1, -1)),
        (1, 8, (1, 1, -3)),
    ],
)
def test_reduce_ratio_extracts_exact_signed_powers_of_two(
    numerator, denominator, expected
):
    assert integer_log._reduce_ratio(numerator, denominator) == expected


def test_reduce_ratio_normalizes_reciprocal_ratio():
    assert integer_log._reduce_ratio(3, 4) == (3, 2, -1)


@pytest.mark.parametrize(
    ("numerator", "denominator"),
    [(5, 7), (7, 5), (1, 8), (64, 3)],
)
def test_reduce_ratio_preserves_value_in_half_open_normalized_range(
    numerator, denominator
):
    reduced_numerator, reduced_denominator, exponent = integer_log._reduce_ratio(
        numerator, denominator
    )

    assert reduced_denominator <= reduced_numerator < 2 * reduced_denominator
    if exponent >= 0:
        assert numerator * reduced_denominator == (
            denominator * reduced_numerator * 2**exponent
        )
    else:
        assert numerator * reduced_denominator * 2 ** (-exponent) == (
            denominator * reduced_numerator
        )


def test_atanh_bounds_enclose_ln_two_after_one_term():
    lower, upper = integer_log._atanh_bounds(1, 3, 1)

    assert 2 * lower == Fraction(2, 3)
    assert 2 * upper == Fraction(25, 36)


def test_atanh_bounds_enclose_ln_three_halves_after_one_term():
    lower, upper = integer_log._atanh_bounds(1, 5, 1)

    assert 2 * lower == Fraction(2, 5)
    assert 2 * upper == Fraction(73, 180)


@pytest.mark.parametrize(
    ("scaled_value", "value_digits", "fractional_digits"),
    [
        (100, 2, 4),
        (101, 2, 4),
        (123, 2, 4),
        (150, 2, 4),
        (199, 2, 4),
        (200, 2, 4),
        (999, 2, 4),
        (1234, 3, 5),
        (1234, 3, 6),
        (10, 1, 3),
        (500, 2, 6),
    ],
)
def test_log10_scaled_matches_floating_point_reference(
    scaled_value, value_digits, fractional_digits
):
    scaled = log10_scaled(scaled_value, value_digits, fractional_digits)
    expected = math.log10(scaled_value / 10**value_digits)

    assert scaled >= 0
    assert abs(scaled / 10**fractional_digits - expected) < (
        0.5 * 10**-fractional_digits + 1e-12
    )


def test_log10_scaled_is_exact_for_powers_of_ten():
    assert log10_scaled(100, 2, 4) == 0
    assert log10_scaled(1000, 3, 4) == 0
    assert log10_scaled(100_000, 4, 4) == 10_000


def test_log10_scaled_agrees_with_published_classic_table():
    assert scaled_to_text(log10_scaled(101, 2, 4), 4) == "0.0043"
    assert scaled_to_text(log10_scaled(150, 2, 4), 4) == "0.1761"
    assert scaled_to_text(log10_scaled(200, 2, 4), 4) == "0.3010"
    assert scaled_to_text(log10_scaled(199, 2, 4), 4) == "0.2989"
    assert scaled_to_text(log10_scaled(999, 2, 4), 4) == "0.9996"


@pytest.mark.parametrize("scaled_value", [0, -5])
def test_log10_scaled_rejects_non_positive_values(scaled_value):
    with pytest.raises(CalculationError, match="^scaled_value must be positive$"):
        log10_scaled(scaled_value, 2, 4)


def test_log10_scaled_rejects_negative_value_digits():
    with pytest.raises(CalculationError, match="^value_digits must be non-negative$"):
        log10_scaled(100, -1, 4)
