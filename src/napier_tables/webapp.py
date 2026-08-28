"""Flask web application for storing logarithm table configurations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from flask import Flask, abort, render_template_string, request
from markupsafe import escape
from sqlalchemy import Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .config import ConfigurationError, TableConfig
from .generation import generate_table
from .historical import (
    HistoricalConfig,
    HistoricalError,
    build_historical_table,
    render_historical_html,
)
from .integer_log import scaled_to_text

MAX_TABLE_ROWS = 5_000


INDEX_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Napier Tables</title>
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
  <style>
    :root {
      color-scheme: light;
      --bg: #f4f1ea;
      --panel: #fffdf8;
      --panel-2: #f8efe2;
      --ink: #1f1b16;
      --muted: #6e6256;
      --accent: #7c4d2b;
      --accent-soft: #c89a6c;
      --border: #d7c8b4;
      --shadow: 0 18px 50px rgba(85, 58, 31, 0.12);
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(200, 154, 108, 0.18), transparent 32%),
        radial-gradient(circle at bottom right, rgba(124, 77, 43, 0.12), transparent 28%),
        var(--bg);
    }

    .shell {
      max-width: 1120px;
      margin: 0 auto;
      padding: 36px 20px 48px;
    }

    .hero {
      display: grid;
      gap: 14px;
      padding: 28px 30px;
      border: 1px solid rgba(124, 77, 43, 0.16);
      border-radius: 24px;
      background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,250,244,0.96));
      box-shadow: var(--shadow);
      margin-bottom: 22px;
    }

    h1 { margin: 0; font-size: clamp(2rem, 4vw, 3.4rem); letter-spacing: -0.04em; }
    .lede { margin: 0; color: var(--muted); font-size: 1.02rem; max-width: 64ch; }

    .grid {
      display: grid;
      grid-template-columns: minmax(320px, 420px) 1fr;
      gap: 20px;
      align-items: start;
    }

    .card {
      border: 1px solid var(--border);
      border-radius: 22px;
      background: var(--panel);
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .card header {
      padding: 18px 20px 16px;
      background: linear-gradient(180deg, #fff, var(--panel-2));
      border-bottom: 1px solid var(--border);
    }

    .card h2 { margin: 0; font-size: 1.2rem; }
    .card p { margin: 6px 0 0; color: var(--muted); }

    form { margin: 0; }
    .form-body { padding: 18px 20px 20px; display: grid; gap: 14px; }
    .fields { display: grid; gap: 12px; }
    .field { display: grid; gap: 6px; }
    label { font-weight: 700; font-size: 0.95rem; }
    input[type="number"] {
      width: 100%;
      padding: 12px 14px;
      border: 1px solid var(--border);
      border-radius: 14px;
      background: #fff;
      color: var(--ink);
      font: inherit;
    }
    input[type="number"]:focus { outline: 2px solid rgba(124, 77, 43, 0.25); outline-offset: 1px; }

    .actions { display: flex; gap: 10px; align-items: center; }
    .button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      border: 0;
      border-radius: 999px;
      padding: 11px 16px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      color: #fff;
      background: linear-gradient(180deg, #8a5a35, #6b4124);
    }
    .button.secondary {
      color: var(--ink);
      background: #efe5d9;
    }

    .list-box { padding: 0; }
    .list-head { padding: 18px 20px 16px; border-bottom: 1px solid var(--border); }
    .list-head h2 { margin: 0; font-size: 1.2rem; }
    .list-head p { margin: 6px 0 0; color: var(--muted); }
    .items { display: grid; gap: 12px; padding: 18px 20px 20px; }
    .empty {
      padding: 20px;
      border: 1px dashed var(--border);
      border-radius: 18px;
      color: var(--muted);
      background: rgba(255,255,255,0.65);
    }

    .item {
      display: grid;
      gap: 12px;
      padding: 16px;
      border: 1px solid var(--border);
      border-radius: 18px;
      background: linear-gradient(180deg, #fff, #fcf7ef);
    }
    .item-title { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }
    .item-title strong { font-size: 1rem; }
    .meta { color: var(--muted); font-size: 0.95rem; }
    .item-actions { display: flex; gap: 8px; flex-wrap: wrap; }
    .link-button {
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 8px 12px;
      background: #fff;
      color: var(--ink);
      text-decoration: none;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }

    .notice { color: var(--muted); font-size: 0.92rem; }

    .field-pair { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

    .card-stack {
      display: grid;
      gap: 20px;
    }

    .table-view { margin-top: 20px; }
    .table-body { padding: 18px 20px 20px; overflow-x: auto; }
    table.log-table {
      width: 100%;
      border-collapse: collapse;
      font-variant-numeric: tabular-nums;
      font-size: 0.95rem;
    }
    table.log-table th, table.log-table td {
      border: 1px solid var(--border);
      padding: 7px 10px;
      text-align: right;
      white-space: nowrap;
    }
    table.log-table thead th {
      background: var(--panel-2);
      position: sticky;
      top: 0;
    }
    table.log-table tbody tr:nth-child(even) { background: rgba(200, 154, 108, 0.07); }
    .error {
      padding: 20px;
      border: 1px solid var(--accent-soft);
      border-radius: 18px;
      color: var(--accent);
      background: rgba(255,255,255,0.7);
    }

    @media (max-width: 900px) {
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <h1>Napier Tables</h1>
      <p class="lede">Create modern or historical logarithm tables with integer-only arithmetic. Modern tables are saved to sqlite; historical tables are generated on the fly.</p>
    </section>

    <div class="grid">
      <div class="card-stack">
        <section class="card">
          <header>
            <h2>Modern table</h2>
            <p>Choose the base, range, and decimal places for a saved configuration.</p>
          </header>
          <form id="create-form" class="form-body" method="post" action="/tables" hx-post="/tables" hx-target="#table-list" hx-swap="outerHTML">
            <div class="fields">
              <div class="field">
                <label for="base">Base</label>
                <input id="base" name="base" type="number" min="2" step="1" value="10" required>
              </div>
              <div class="field-pair">
                <div class="field">
                  <label for="start">Start</label>
                  <input id="start" name="start" type="number" min="1" step="1" value="1" required>
                </div>
                <div class="field">
                  <label for="end">End</label>
                  <input id="end" name="end" type="number" min="1" step="1" value="100" required>
                </div>
              </div>
              <div class="field">
                <label for="log_precision">Decimal places</label>
                <input id="log_precision" name="log_precision" type="number" min="1" step="1" value="4" required>
              </div>
            </div>
            <div class="actions">
              <button class="button" type="submit">Save table</button>
              <span class="notice">Stored in sqlite3 through SQLAlchemy.</span>
            </div>
          </form>
        </section>

        <section class="card">
          <header>
            <h2>Historical Bragg table</h2>
            <p>1950s proportional layout: argument rows with 10 mantissa sub-columns per row. Fixed decade from N resolution.</p>
          </header>
          <form id="historical-form" class="form-body" method="post" action="/historical" hx-post="/historical" hx-target="#table-view" hx-swap="outerHTML">
            <div class="fields">
              <div class="field">
                <label for="hist-base">Base</label>
                <input id="hist-base" name="base" type="number" min="2" step="1" value="10" required>
              </div>
              <div class="field-pair">
                <div class="field">
                  <label for="resolution">N resolution</label>
                  <input id="resolution" name="resolution" type="number" min="0" step="1" value="0" required>
                  <span class="notice">0 → 1–9 · 1 → 10–99 · 2 → 100–999</span>
                </div>
                <div class="field">
                  <label for="hist-log_precision">Log precision</label>
                  <input id="hist-log_precision" name="log_precision" type="number" min="1" step="1" value="4" required>
                </div>
              </div>
            </div>
            <div class="actions">
              <button class="button" type="submit">Generate table</button>
              <span class="notice">Rendered on the fly, not saved.</span>
            </div>
          </form>
        </section>
      </div>

      {{ table_list|safe }}
    </div>

    {{ table_view|safe }}
  </div>
</body>
</html>
"""

TABLE_LIST_TEMPLATE = """<section id="table-list" class="card list-box">
  <div class="list-head">
    <h2>Created tables</h2>
    <p>Use edit and delete actions directly in the list.</p>
  </div>
  <div class="items">
    {content}
  </div>
</section>
"""

ROW_TEMPLATE = """<article class="item" data-table-id="{id}">
  <div class="item-title">
    <strong>Table {id}</strong>
    <span class="meta">Base {base} · {start}–{end} · Log precision {log_precision}</span>
  </div>
  <div class="item-actions">
    <button class="button" hx-get="/tables/{id}/table" hx-target="#table-view" hx-swap="outerHTML">Show table</button>
    <button class="link-button" hx-get="/tables/{id}/edit" hx-target="[data-table-id='{id}']" hx-swap="outerHTML">Edit</button>
    <button class="link-button" hx-delete="/tables/{id}" hx-target="#table-list" hx-swap="outerHTML" hx-confirm="Delete this table?">Delete</button>
  </div>
</article>
"""

TABLE_VIEW_TEMPLATE = """<section id="table-view" class="card table-view">
  <div class="list-head">
    <h2>{heading}</h2>
    <p>{subheading}</p>
  </div>
  <div class="table-body">
    {content}
  </div>
</section>
"""

EMPTY_TABLE_VIEW = TABLE_VIEW_TEMPLATE.format(
    heading="Generated table",
    subheading="Choose a saved configuration and select Show table.",
    content='<div class="empty">No table is being shown yet.</div>',
)

EDIT_ROW_TEMPLATE = \"\"\"<article class=\"item\" data-table-id=\"{id}\">
  <form hx-put=\"/tables/{id}\" hx-target=\"#table-list\" hx-swap=\"outerHTML\">
    <div class=\"item-title\">
      <strong>Editing table {id}</strong>
      <span class=\"meta\">SQLite record #{id}</span>
    </div>
    <div class=\"fields\">
      <div class=\"field\">
        <label for=\"base-{id}\">Base</label>
        <input id=\"base-{id}\" name=\"base\" type=\"number\" min=\"2\" step=\"1\" value=\"{base}\" required>
      </div>
      <div class=\"field-pair\">
        <div class=\"field\">
          <label for=\"start-{id}\">Start</label>
          <input id=\"start-{id}\" name=\"start\" type=\"number\" min=\"1\" step=\"1\" value=\"{start}\" required>
        </div>
        <div class=\"field\">
          <label for=\"end-{id}\">End</label>
          <input id=\"end-{id}\" name=\"end\" type=\"number\" min=\"1\" step=\"1\" value=\"{end}\" required>
        </div>
      </div>
      <div class=\"field\">
        <label for=\"log_precision-{id}\">Decimal places</label>
        <input id=\"log_precision-{id}\" name=\"log_precision\" type=\"number\" min=\"1\" step=\"1\" value=\"{log_precision}\" required>
      </div>
    </div>
    <div class=\"item-actions\">
      <button class=\"button\" type=\"submit\">Update</button>
      <button class=\"link-button\" hx-get=\"/tables/{id}\" hx-target=\"[data-table-id='{id}']\" hx-swap=\"outerHTML\">Cancel</button>
    </div>
  </form>
</article>
\"\"\"
EDIT_ROW_TEMPLATE = """<article class="item" data-table-id="{id}">
  <form hx-put="/tables/{id}" hx-target="#table-list" hx-swap="outerHTML">
    <div class="item-title">
      <strong>Editing table {id}</strong>
      <span class="meta">SQLite record #{id}</span>
    </div>
    <div class="fields">
      <div class="field">
        <label for="base-{id}">Base</label>
        <input id="base-{id}" name="base" type="number" min="2" step="1" value="{base}" required>
      </div>
      <div class="field-pair">
        <div class="field">
          <label for="start-{id}">Start</label>
          <input id="start-{id}" name="start" type="number" min="1" step="1" value="{start}" required>
        </div>
        <div class="field">
          <label for="end-{id}">End</label>
          <input id="end-{id}" name="end" type="number" min="1" step="1" value="{end}" required>
        </div>
      </div>
      <div class="field">
        <label for="precision-{id}">Precision</label>
        <input id="precision-{id}" name="precision" type="number" min="1" step="1" value="{precision}" required>
      </div>
      <div class="field">
        <label for="log_precision-{id}">Log precision</label>
        <input id="log_precision-{id}" name="log_precision" type="number" min="1" step="1" value="{log_precision}" required>
      </div>
    </div>
    <div class="item-actions">
      <button class="button" type="submit">Update</button>
      <button class="link-button" hx-get="/tables/{id}" hx-target="[data-table-id='{id}']" hx-swap="outerHTML">Cancel</button>
    </div>
  </form>
</article>
"""


class Base(DeclarativeBase):
    pass


class TableSpec(Base):
    __tablename__ = "table_specs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    precision: Mapped[int] = mapped_column(Integer, nullable=False)
    log_precision: Mapped[int] = mapped_column(Integer, nullable=False)
    base: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    start: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    end: Mapped[int] = mapped_column(Integer, nullable=False, default=1_000)


def _render_table_list(rows: list[TableSpec]) -> str:
    if not rows:
        content = '<div class="empty">No tables have been created yet.</div>'
    else:
        content = "\n    ".join(_render_row(row) for row in rows)
    return TABLE_LIST_TEMPLATE.format(content=content)


def _render_row(row: TableSpec) -> str:
    return ROW_TEMPLATE.format(
        id=row.id,
        precision=row.precision,
        log_precision=row.log_precision,
        base=row.base,
        start=row.start,
        end=row.end,
    )


def _render_edit_row(row: TableSpec) -> str:
    return EDIT_ROW_TEMPLATE.format(
        id=row.id,
        precision=row.precision,
        log_precision=row.log_precision,
        base=row.base,
        start=row.start,
        end=row.end,
    )


def _spec_to_config(row: TableSpec) -> TableConfig:
    return TableConfig(
        base=row.base,
        fractional_digits=row.log_precision,
        start=row.start,
        end=row.end,
    )


def _render_generated_table(row: TableSpec) -> str:
    """Generate the table for ``row`` and render it, or report why it cannot be."""
    row_count = row.end - row.start + 1
    heading = f"Table {row.id}"
    subheading = (
        f"Base {row.base} · inputs {row.start}–{row.end} · "
        f"{row.log_precision} decimal places · {row_count} rows"
    )

    if row_count > MAX_TABLE_ROWS:
        return TABLE_VIEW_TEMPLATE.format(
            heading=heading,
            subheading=subheading,
            content=(
                f'<div class="error">This configuration covers {row_count} rows. '
                f"Showing at most {MAX_TABLE_ROWS} rows at a time keeps the page "
                "responsive, so narrow the input range to display it.</div>"
            ),
        )

    try:
        table = generate_table(_spec_to_config(row))
    except ConfigurationError as exc:
        return TABLE_VIEW_TEMPLATE.format(
            heading=heading,
            subheading=subheading,
            content=f'<div class="error">{escape(str(exc))}</div>',
        )

    body = "\n".join(
        f"<tr><td>{entry.input_value}</td>"
        f"<td>{scaled_to_text(entry.scaled_value, entry.fractional_digits)}</td></tr>"
        for entry in table.rows
    )
    content = (
        '<table class="log-table">'
        f"<thead><tr><th>N</th><th>log<sub>{row.base}</sub> N</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )
    return TABLE_VIEW_TEMPLATE.format(
        heading=heading, subheading=subheading, content=content
    )


def _render_page(rows: list[TableSpec], table_view: str = EMPTY_TABLE_VIEW) -> str:
    return render_template_string(
        INDEX_TEMPLATE,
        table_list=_render_table_list(rows),
        table_view=table_view,
    )


def _parse_positive_int(value: str, field_name: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a positive integer") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be a positive integer")
    return parsed


def _parse_spec_form() -> dict[str, int]:
    """Read and validate every table field from the submitted form."""
    fields = {
        name: _parse_positive_int(request.form.get(name, ""), name)
        for name in ("precision", "log_precision", "base", "start", "end")
    }
    if fields["base"] < 2:
        raise ValueError("base must be at least 2")
    if fields["end"] < fields["start"]:
        raise ValueError("end must be greater than or equal to start")
    return fields


def _is_htmx_request() -> bool:
    return request.headers.get("HX-Request", "").lower() == "true"


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    default_database = Path(app.instance_path) / "tables.sqlite3"
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE_URL=f"sqlite+pysqlite:///{default_database}",
        DATABASE_PATH=str(default_database),
    )
    if test_config:
        app.config.update(test_config)

    database_url = app.config["DATABASE_URL"]
    if database_url.startswith("sqlite+pysqlite:///"):
        database_path = database_url.removeprefix("sqlite+pysqlite:///")
        app.config["DATABASE_PATH"] = database_path
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(database_url, future=True)
    Base.metadata.create_all(engine)
    SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)

    def get_session() -> Session:
        return SessionFactory()

    @app.get("/")
    def index() -> str:
        with get_session() as session:
            rows = session.scalars(select(TableSpec).order_by(TableSpec.id)).all()
        return _render_page(list(rows))

    @app.post("/tables")
    def create_table() -> str:
        try:
            fields = _parse_spec_form()
        except ValueError:
            abort(400)

        with get_session() as session:
            record = TableSpec(**fields)
            session.add(record)
            session.commit()
            rows = session.scalars(select(TableSpec).order_by(TableSpec.id)).all()

        rendered_list = _render_table_list(list(rows))
        if _is_htmx_request():
            return rendered_list
        return _render_page(list(rows))

    @app.get("/tables/<int:table_id>/edit")
    def edit_table(table_id: int) -> str:
        with get_session() as session:
            row = session.get(TableSpec, table_id)
        if row is None:
            abort(404)
        return _render_edit_row(row)

    @app.get("/tables/<int:table_id>")
    def view_table(table_id: int) -> str:
        with get_session() as session:
            row = session.get(TableSpec, table_id)
        if row is None:
            abort(404)
        return _render_row(row)

    @app.get("/tables/<int:table_id>/table")
    def show_generated_table(table_id: int) -> str:
        with get_session() as session:
            row = session.get(TableSpec, table_id)
        if row is None:
            abort(404)

        rendered_view = _render_generated_table(row)
        if _is_htmx_request():
            return rendered_view

        with get_session() as session:
            rows = session.scalars(select(TableSpec).order_by(TableSpec.id)).all()
        return _render_page(list(rows), table_view=rendered_view)

    @app.put("/tables/<int:table_id>")
    def update_table(table_id: int) -> str:
        try:
            fields = _parse_spec_form()
        except ValueError:
            abort(400)

        with get_session() as session:
            row = session.get(TableSpec, table_id)
            if row is None:
                abort(404)
            for name, value in fields.items():
                setattr(row, name, value)
            session.commit()
            rows = session.scalars(select(TableSpec).order_by(TableSpec.id)).all()

        return _render_table_list(list(rows))

    @app.delete("/tables/<int:table_id>")
    def delete_table(table_id: int) -> str:
        with get_session() as session:
            row = session.get(TableSpec, table_id)
            if row is None:
                abort(404)
            session.delete(row)
            session.commit()
            rows = session.scalars(select(TableSpec).order_by(TableSpec.id)).all()

        return _render_table_list(list(rows))

    return app
