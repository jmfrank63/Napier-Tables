import pytest

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
