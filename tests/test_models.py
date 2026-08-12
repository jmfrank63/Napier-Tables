from dataclasses import FrozenInstanceError

import pytest

from napier_tables import ConfigurationError, LogRow, LogTable, TableConfig


def test_valid_row_and_table_expose_immutable_fields_and_values():
    config = TableConfig(start=1, end=3, fractional_digits=4)
    rows = (
        LogRow(input_value=1, scaled_value=0, fractional_digits=4),
        LogRow(input_value=2, scaled_value=3010, fractional_digits=4),
        LogRow(input_value=3, scaled_value=4771, fractional_digits=4),
    )

    table = LogTable(config=config, rows=rows)

    assert table.config == config
    assert table.rows == rows
    assert table.values() == (1, 2, 3)


def test_log_row_is_frozen_and_slotted():
    row = LogRow(input_value=1, scaled_value=0, fractional_digits=4)

    assert not hasattr(row, "__dict__")
    with pytest.raises(FrozenInstanceError):
        row.input_value = 2


def test_log_table_is_frozen_and_slotted():
    table = LogTable(
        config=TableConfig(start=1, end=1),
        rows=(LogRow(input_value=1, scaled_value=0, fractional_digits=4),),
    )

    assert not hasattr(table, "__dict__")
    with pytest.raises(FrozenInstanceError):
        table.rows = ()


def test_log_row_rejects_non_positive_input():
    with pytest.raises(ConfigurationError, match="input_value must be positive"):
        LogRow(input_value=0, scaled_value=0, fractional_digits=4)


def test_log_table_rejects_precision_mismatch():
    config = TableConfig(fractional_digits=4)
    row = LogRow(input_value=1, scaled_value=0, fractional_digits=3)

    with pytest.raises(ConfigurationError, match="fractional_digits must match"):
        LogTable(config=config, rows=(row,))


def test_log_table_rejects_duplicate_inputs():
    config = TableConfig(start=1, end=2)
    rows = (
        LogRow(input_value=1, scaled_value=0, fractional_digits=4),
        LogRow(input_value=1, scaled_value=0, fractional_digits=4),
    )

    with pytest.raises(ConfigurationError, match="strictly increasing"):
        LogTable(config=config, rows=rows)


def test_log_table_rejects_non_increasing_rows():
    config = TableConfig(start=1, end=3)
    rows = (
        LogRow(input_value=2, scaled_value=3010, fractional_digits=4),
        LogRow(input_value=1, scaled_value=0, fractional_digits=4),
    )

    with pytest.raises(ConfigurationError, match="strictly increasing"):
        LogTable(config=config, rows=rows)
