import pytest

from napier_tables.config import ConfigurationError, TableConfig
from napier_tables.generation import generate_rows, generate_table
from napier_tables.integer_log import calculate_row


def test_generate_table_covers_the_whole_inclusive_range():
    table = generate_table(TableConfig(base=10, fractional_digits=4, start=1, end=10))

    assert table.values() == tuple(range(1, 11))


def test_generate_table_rows_match_independent_row_calculation():
    config = TableConfig(base=10, fractional_digits=4, start=1, end=20)

    table = generate_table(config)

    assert table.rows == tuple(calculate_row(value, 10, 4) for value in range(1, 21))


def test_generate_table_preserves_input_order_under_threading():
    config = TableConfig(base=10, fractional_digits=5, start=1, end=60, workers=8)

    table = generate_table(config)

    assert table.values() == tuple(range(1, 61))


def test_generate_table_result_is_independent_of_worker_count():
    single = generate_table(
        TableConfig(base=10, fractional_digits=4, start=1, end=40, workers=1)
    )
    many = generate_table(
        TableConfig(base=10, fractional_digits=4, start=1, end=40, workers=8)
    )

    assert single.rows == many.rows


def test_generate_table_carries_its_configuration():
    config = TableConfig(base=2, fractional_digits=3, start=1, end=8)

    table = generate_table(config)

    assert table.config is config
    assert table.rows[-1].scaled_value == 3_000


def test_generate_rows_returns_a_single_row_range():
    rows = generate_rows(TableConfig(base=10, fractional_digits=4, start=5, end=5))

    assert len(rows) == 1
    assert rows[0].input_value == 5


def test_generate_table_rejects_invalid_configuration():
    with pytest.raises(ConfigurationError):
        generate_table(TableConfig(base=1, fractional_digits=4, start=1, end=10))
    with pytest.raises(ConfigurationError):
        generate_table(TableConfig(base=10, fractional_digits=4, start=0, end=10))
