"""Historical proportional-logarithm-table layout (1950s school-table format).

Implements the proportional layout used by printed 1950s-era log tables:
rows keyed by the leading significant digits (the "argument"), with 10
mantissa sub-columns for each trailing unit digit.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from .config import ConfigurationError, TableConfig
from .generation import generate_rows
from .integer_log import scaled_to_text


class HistoricalError(ValueError):
    """Raised when a historical table configuration or construction is invalid."""


@dataclass(frozen=True, slots=True)
class HistoricalConfig:
    """Configuration for a historical-format logarithm table.

    Parameters
    ----------
    resolution : int
        The N resolution (decade = 10**r to 10**(r+1), upper bound excluded).
    log_precision : int
        Number of fractional decimal digits for the log mantissa.
    base : int
        Logarithm base (must be at least 2).
    """

    resolution: int = 0
    log_precision: int = 4
    base: int = 10

    def validate(self) -> None:
        """Raise HistoricalError if any field is invalid."""
        if self.resolution < 0:
            raise HistoricalError("resolution must be non-negative")
        if self.log_precision < 1:
            raise HistoricalError("log_precision must be at least 1")
        if self.base < 2:
            raise HistoricalError("base must be at least 2")

    def decade(self) -> tuple[int, int]:
        """Return the (inclusive_start, exclusive_end) for this resolution."""
        return decade_range(self.resolution)


def decade_range(resolution: int) -> tuple[int, int]:
    """Map N resolution to a fixed decade (start, end) with end exclusive.

    Resolution r => decade [10**r, 10**(r+1)).
    ``range(*decade_range(r))`` never yields ``10**(r+1)``.
    """
    if resolution < 0:
        raise HistoricalError("resolution must be non-negative")
    return (10**resolution, 10 ** (resolution + 1))


@dataclass(frozen=True, slots=True)
class ProportionalRow:
    """One row in a proportional-format logarithm table.

    The *argument* (leading significant digits of N) is stored as text for
    display.  The ten *columns* are the mantissa text for each trailing
    digit 0–9.
    """

    argument: str
    columns: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class HistoricalTable:
    """An immutable proportional-logarithm-table layout."""

    config: HistoricalConfig
    rows: tuple[ProportionalRow, ...]

    def __post_init__(self) -> None:
        for row in self.rows:
            if len(row.columns) != 10:
                raise HistoricalError(
                    "each proportional row must have exactly 10 sub-columns"
                )


def build_historical_table(config: HistoricalConfig) -> HistoricalTable:
    """Build a proportional-layout historical table from the integer engine.

    For resolution *r* the table covers values ``10**(r+1)`` … ``10**(r+2) - 1``
    (the decade expanded by one decimal digit).  Rows are grouped by the
    leading digit(s) — the argument — and each row shows the mantissa digits
    for trailing digit 0–9.
    """
    config.validate()
    start, end = config.decade()

    # The actual N values to compute logs for are:
    #   argument * 10 + trailing_digit
    # where argument ranges over [10**r, 10**(r+1)) and trailing digit 0-9.
    calc_start = start * 10
    calc_end = end * 10 - 1

    table_config = TableConfig(
        base=config.base,
        fractional_digits=config.log_precision,
        start=calc_start,
        end=calc_end,
    )
    log_rows = generate_rows(table_config)

    # Group by argument (leading digits = N // 10).
    groups: dict[int, dict[int, str]] = {}
    for row in log_rows:
        n = row.input_value
        argument = n // 10
        trailing = n % 10
        mantissa = scaled_to_text(row.scaled_value, row.fractional_digits)
        groups.setdefault(argument, {})[trailing] = mantissa

    proportional_rows: list[ProportionalRow] = []
    for arg in range(start, end):
        cols = tuple(groups.get(arg, {}).get(d, "") for d in range(10))
        proportional_rows.append(
            ProportionalRow(argument=str(arg), columns=cols)
        )

    return HistoricalTable(config=config, rows=tuple(proportional_rows))


def _mantissa_only(text: str) -> str:
    """Return the fractional (mantissa) part of a decimal log value.

    ``"1.0414"`` → ``"0414"``, ``"0.3010"`` → ``"3010"``, ``"0.0000"`` → ``"0000"``.
    """
    if "." in text:
        return text.split(".", 1)[1]
    return text


def render_historical_html(
    table: HistoricalTable, title: str | None = None
) -> str:
    """Render a historical-format table as a deterministic HTML fragment.

    The output is a ``<table class="log-table historical">`` element with
    argument and digit column headers, one ``<tr>`` per *ProportionalRow*,
    mantissa-only sub-columns, and the leading characteristic shown per row.
    All user-originated text is HTML-escaped.
    """
    import html

    lines: list[str] = []
    lines.append('<table class="log-table historical">')
    lines.append("<thead><tr><th>N</th>")
    for d in range(10):
        lines.append(f"<th>{d}</th>")
    lines.append("</tr></thead>")
    lines.append("<tbody>")

    for prop_row in table.rows:
        arg = html.escape(prop_row.argument)
        lines.append(f"<tr><th>{arg}</th>")
        for col in prop_row.columns:
            # Display only the mantissa (fractional digits).
            mant = html.escape(_mantissa_only(col))
            lines.append(f"<td>{mant}</td>")
        lines.append("</tr>")

    lines.append("</tbody>")
    lines.append("</table>")

    html_fragment = "\n".join(lines)
    if title:
        escaped_title = html.escape(title)
        html_fragment = f"<h3>{escaped_title}</h3>\n{html_fragment}"
    return html_fragment