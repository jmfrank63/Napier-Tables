"""Threaded generation of immutable logarithm tables."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from .config import TableConfig
from .integer_log import calculate_row
from .models import LogRow, LogTable


def generate_rows(config: TableConfig) -> tuple[LogRow, ...]:
    """Calculate every row for ``config`` independently and in input order.

    Each row is calculated from its own input value only, so no rounding state
    is shared between rows and the result does not depend on worker count.
    """
    config.validate()
    values = range(config.start, config.end + 1)

    with ThreadPoolExecutor(max_workers=config.workers) as executor:
        rows = executor.map(
            lambda value: calculate_row(
                value, config.base, config.fractional_digits
            ),
            values,
        )
        return tuple(rows)


def generate_table(config: TableConfig) -> LogTable:
    """Build the immutable table described by ``config``."""
    return LogTable(config=config, rows=generate_rows(config))
