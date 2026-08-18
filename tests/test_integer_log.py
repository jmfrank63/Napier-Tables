from fractions import Fraction

import pytest

from napier_tables import integer_log
from napier_tables.integer_log import CalculationError, round_ratio, scaled_to_text


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


def test_ln_bounds_return_zero_for_one():
    assert integer_log._ln_bounds(1, 10_000) == (0, 0)


def test_ln_bounds_enclose_natural_log_of_two():
    lower, upper = integer_log._ln_bounds(2, 10_000)

    # ln(2) = 0.693147...
    assert lower <= 6_931 <= upper
    assert upper - lower <= 1


def test_ln_bounds_enclose_natural_log_of_ten():
    lower, upper = integer_log._ln_bounds(10, 10_000)

    # ln(10) = 2.302585...
    assert lower <= 23_025 <= upper
    assert upper - lower <= 1


@pytest.mark.parametrize("value", [0, -1])
def test_ln_bounds_reject_values_below_one(value):
    with pytest.raises(CalculationError, match="^value must be at least 1$"):
        integer_log._ln_bounds(value, 10_000)


def test_ratio_bounds_enclose_reference_logarithm():
    lower, upper = integer_log._ratio_bounds(2, 10, 10_000)

    # log10(2) = 0.301029...
    assert lower <= 3_010 <= upper


def test_calculate_log_scaled_returns_zero_for_one():
    assert integer_log.calculate_log_scaled(1, 10, 10_000) == 0


def test_calculate_log_scaled_returns_scale_for_base_itself():
    assert integer_log.calculate_log_scaled(10, 10, 10_000) == 10_000
    assert integer_log.calculate_log_scaled(2, 2, 10_000) == 10_000


@pytest.mark.parametrize(
    ("value", "expected"),
    [(2, 10_000), (4, 20_000), (8, 30_000), (1_024, 100_000)],
)
def test_calculate_log_scaled_is_exact_for_powers_of_two_in_base_two(value, expected):
    assert integer_log.calculate_log_scaled(value, 2, 10_000) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [(2, 3_010), (3, 4_771), (7, 8_451), (100, 20_000), (999, 29_996)],
)
def test_calculate_log_scaled_matches_base_ten_reference_values(value, expected):
    # Reference mantissas taken from published four-figure logarithm tables.
    assert integer_log.calculate_log_scaled(value, 10, 10_000) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [(2, 30_103), (3, 47_712), (7, 84_510)],
)
def test_calculate_log_scaled_matches_five_figure_reference_values(value, expected):
    assert integer_log.calculate_log_scaled(value, 10, 100_000) == expected


def test_calculate_log_scaled_rejects_invalid_inputs():
    with pytest.raises(CalculationError, match="^value must be at least 1$"):
        integer_log.calculate_log_scaled(0, 10, 10_000)
    with pytest.raises(CalculationError, match="^base must be at least 2$"):
        integer_log.calculate_log_scaled(2, 1, 10_000)
    with pytest.raises(CalculationError, match="^scale must be positive$"):
        integer_log.calculate_log_scaled(2, 10, 0)


def test_calculate_row_builds_model_at_requested_precision():
    row = integer_log.calculate_row(3, 10, 4)

    assert row.input_value == 3
    assert row.scaled_value == 4_771
    assert row.fractional_digits == 4
    assert scaled_to_text(row.scaled_value, row.fractional_digits) == "0.4771"


def test_calculate_row_supports_zero_fractional_digits():
    row = integer_log.calculate_row(1_000, 10, 0)

    assert row.scaled_value == 3
    assert row.fractional_digits == 0


def test_calculate_row_rejects_invalid_inputs():
    with pytest.raises(CalculationError, match="^value must be at least 1$"):
        integer_log.calculate_row(0, 10, 4)
    with pytest.raises(CalculationError, match="^base must be at least 2$"):
        integer_log.calculate_row(3, 1, 4)
    with pytest.raises(CalculationError, match="^fractional_digits must be non-negative$"):
        integer_log.calculate_row(3, 10, -1)


def test_calculate_row_is_independent_of_calculation_order():
    ascending = [integer_log.calculate_row(value, 10, 5) for value in range(1, 40)]
    descending = [integer_log.calculate_row(value, 10, 5) for value in range(39, 0, -1)]

    assert ascending == list(reversed(descending))
