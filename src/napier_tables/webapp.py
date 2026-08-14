"""Flask web application for storing logarithm table configurations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from flask import Flask, abort, render_template_string, request
from sqlalchemy import Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


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

    @media (max-width: 900px) {
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <h1>Napier Tables</h1>
      <p class="lede">Create and manage logarithm table configurations with a minimal htmx interface and sqlite-backed persistence.</p>
    </section>

    <div class="grid">
      <section class="card">
        <header>
          <h2>Create a table</h2>
          <p>Choose the precision and logarithm precision for a saved configuration.</p>
        </header>
        <form id="create-form" class="form-body" method="post" action="/tables" hx-post="/tables" hx-target="#table-list" hx-swap="outerHTML">
          <div class="fields">
            <div class="field">
              <label for="precision">Precision</label>
              <input id="precision" name="precision" type="number" min="1" step="1" required>
            </div>
            <div class="field">
              <label for="log_precision">Log precision</label>
              <input id="log_precision" name="log_precision" type="number" min="1" step="1" required>
            </div>
          </div>
          <div class="actions">
            <button class="button" type="submit">Save table</button>
            <span class="notice">Stored in sqlite3 through SQLAlchemy.</span>
          </div>
        </form>
      </section>

      {{ table_list|safe }}
    </div>
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
    <span class="meta">Precision {precision} · Log precision {log_precision}</span>
  </div>
  <div class="item-actions">
    <button class="link-button" hx-get="/tables/{id}/edit" hx-target="[data-table-id='{id}']" hx-swap="outerHTML">Edit</button>
    <button class="link-button" hx-delete="/tables/{id}" hx-target="#table-list" hx-swap="outerHTML" hx-confirm="Delete this table?">Delete</button>
  </div>
</article>
"""

EDIT_ROW_TEMPLATE = """<article class="item" data-table-id="{id}">
  <form hx-put="/tables/{id}" hx-target="#table-list" hx-swap="outerHTML">
    <div class="item-title">
      <strong>Editing table {id}</strong>
      <span class="meta">SQLite record #{id}</span>
    </div>
    <div class="fields">
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


def _render_table_list(rows: list[TableSpec]) -> str:
    if not rows:
        content = '<div class="empty">No tables have been created yet.</div>'
    else:
        content = "\n    ".join(
            ROW_TEMPLATE.format(
                id=row.id,
                precision=row.precision,
                log_precision=row.log_precision,
            )
            for row in rows
        )
    return TABLE_LIST_TEMPLATE.format(content=content)


def _render_page(rows: list[TableSpec]) -> str:
    return render_template_string(INDEX_TEMPLATE, table_list=_render_table_list(rows))


def _parse_positive_int(value: str, field_name: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a positive integer") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be a positive integer")
    return parsed


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
        app.config["DATABASE_PATH"] = database_url.removeprefix(
            "sqlite+pysqlite:///"
        )

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
            precision = _parse_positive_int(request.form.get("precision", ""), "precision")
            log_precision = _parse_positive_int(
                request.form.get("log_precision", ""), "log_precision"
            )
        except ValueError:
            abort(400)

        with get_session() as session:
            record = TableSpec(precision=precision, log_precision=log_precision)
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
        return EDIT_ROW_TEMPLATE.format(
            id=row.id, precision=row.precision, log_precision=row.log_precision
        )

    @app.get("/tables/<int:table_id>")
    def view_table(table_id: int) -> str:
        with get_session() as session:
            row = session.get(TableSpec, table_id)
        if row is None:
            abort(404)
        return ROW_TEMPLATE.format(
            id=row.id, precision=row.precision, log_precision=row.log_precision
        )

    @app.put("/tables/<int:table_id>")
    def update_table(table_id: int) -> str:
        try:
            precision = _parse_positive_int(request.form.get("precision", ""), "precision")
            log_precision = _parse_positive_int(
                request.form.get("log_precision", ""), "log_precision"
            )
        except ValueError:
            abort(400)

        with get_session() as session:
            row = session.get(TableSpec, table_id)
            if row is None:
                abort(404)
            row.precision = precision
            row.log_precision = log_precision
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
