"""Immutable configuration for logarithm table generation."""

from dataclasses import dataclass


class ConfigurationError(ValueError):
    """Raised when a table configuration contains an invalid value."""


@dataclass(frozen=True, slots=True)
class TableConfig:
    """Parameters that define a logarithm table."""

    base: int = 10
    fractional_digits: int = 4
    start: int = 1
    end: int = 1000
    workers: int | None = None

    def validate(self) -> None:
        """Raise ``ConfigurationError`` if any configuration value is invalid."""
        if self.base < 2:
            raise ConfigurationError("base must be at least 2")
        if self.fractional_digits < 0:
            raise ConfigurationError("fractional_digits must be non-negative")
        if self.start < 1:
            raise ConfigurationError("start must be at least 1")
        if self.end < self.start:
            raise ConfigurationError("end must be greater than or equal to start")
        if self.workers is not None and self.workers < 1:
            raise ConfigurationError("workers must be at least 1 or None")
