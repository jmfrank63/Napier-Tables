"""Immutable models for generated logarithm tables."""

from dataclasses import dataclass

from .config import ConfigurationError, TableConfig


@dataclass(frozen=True, slots=True)
class LogRow:
    """One scaled logarithm value for a positive integer input."""

    input_value: int
    scaled_value: int
    fractional_digits: int

    def __post_init__(self) -> None:
        if self.input_value <= 0:
            raise ConfigurationError("input_value must be positive")


@dataclass(frozen=True, slots=True)
class LogTable:
    """An ordered, immutable collection of logarithm rows."""

    config: TableConfig
    rows: tuple[LogRow, ...]

    def __post_init__(self) -> None:
        for row in self.rows:
            if row.fractional_digits != self.config.fractional_digits:
                raise ConfigurationError(
                    "fractional_digits must match table configuration"
                )

        if any(
            current.input_value <= previous.input_value
            for previous, current in zip(self.rows, self.rows[1:])
        ):
            raise ConfigurationError("rows must be strictly increasing")

    def values(self) -> tuple[int, ...]:
        """Return the input values in table order."""
        return tuple(row.input_value for row in self.rows)
