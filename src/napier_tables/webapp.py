"""Flask web application for storing logarithm table configurations."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from flask import Flask, abort, render_template_string, request
from sqlalchemy import Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .integer_log import log10_scaled, round_ratio, scaled_to_text


BASE_CSS = """
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
    .link-button:disabled { opacity: 0.4; cursor: default; }

    .notice { color: var(--muted); font-size: 0.92rem; }

    @media (max-width: 900px) {
      .grid { grid-template-columns: 1fr; }
    }
"""

BOOK_CSS = """
    .book-shell {
      max-width: 1180px;
      margin: 0 auto;
      padding: 36px 20px 60px;
    }

    .book { display: grid; gap: 18px; }
    @keyframes book-appear {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: none; }
    }
    .book { animation: book-appear 260ms ease; }

    .zoom-bar {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 8px;
      margin-bottom: 2px;
    }
    .zoom-bar .link-button { padding: 6px 14px; }
    .zoom-level {
      min-width: 52px;
      text-align: center;
      color: var(--muted);
      font-size: 0.9rem;
      font-variant-numeric: tabular-nums;
    }

    .book-toolbar {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: baseline;
      flex-wrap: wrap;
    }
    .book-toolbar strong { font-size: 1.15rem; }

    .book-spread { display: grid; gap: 24px; }
    .book-spread.two {
      grid-template-columns: repeat(2, max-content);
      justify-content: center;
      gap: 0;
      position: relative;
      border-radius: 6px;
      background: linear-gradient(90deg, #fffdf8, #faf3e6);
      box-shadow: 0 26px 60px rgba(85, 58, 31, 0.2);
    }
    .book-spread.two::after {
      content: "";
      position: absolute;
      left: 50%;
      top: 8px;
      bottom: 8px;
      width: 3px;
      transform: translateX(-50%);
      z-index: 1;
      background:
        linear-gradient(90deg, rgba(124, 77, 43, 0.05), rgba(124, 77, 43, 0.35), rgba(124, 77, 43, 0.05));
      border-radius: 2px;
    }

    .book-page {
      width: max-content;
      padding: 22px 20px 26px;
      border: 1px solid var(--border);
      border-radius: 4px 14px 14px 4px;
      background:
        linear-gradient(90deg, rgba(200, 154, 108, 0.1), transparent 26px),
        linear-gradient(180deg, #fffdf8, #faf3e6);
      box-shadow: 0 16px 40px rgba(85, 58, 31, 0.14);
    }
    .book-spread:not(.two) .book-page { margin: 0 auto; }
    .book-spread.two .book-page { border: 0; border-radius: 0; box-shadow: none; }
    .book-spread.two .book-page:first-child {
      border-radius: 14px 0 0 14px;
      background:
        linear-gradient(90deg, rgba(200, 154, 108, 0.12), transparent 30px),
        linear-gradient(270deg, rgba(124, 77, 43, 0.16), transparent 48px),
        linear-gradient(180deg, #fffdf8, #faf3e6);
    }
    .book-spread.two .book-page:last-child {
      border-radius: 0 14px 14px 0;
      background:
        linear-gradient(270deg, rgba(200, 154, 108, 0.12), transparent 30px),
        linear-gradient(90deg, rgba(124, 77, 43, 0.16), transparent 48px),
        linear-gradient(180deg, #fffdf8, #faf3e6);
    }
    .book-page h3 {
      margin: 0 0 2px;
      text-align: center;
      font-weight: 400;
      font-style: italic;
      font-size: 0.95rem;
      color: var(--muted);
    }
    .legend {
      margin: 0 0 10px;
      text-align: center;
      font-size: 0.78rem;
      font-style: italic;
      color: var(--muted);
    }

    .log-table {
      width: auto;
      table-layout: fixed;
      border-collapse: collapse;
      font-variant-numeric: tabular-nums;
      font-size: 0.88rem;
    }
    .log-table col.col-n { width: var(--n-width); }
    .log-table col.col-value { width: var(--value-width); }
    .log-table thead th:first-child { text-align: right; }
    .log-table th,
    .log-table td {
      border: 1px solid rgba(215, 200, 180, 0.7);
      padding: 3px 6px;
      text-align: right;
      white-space: nowrap;
    }
    .log-table thead th {
      background: rgba(124, 77, 43, 0.08);
      font-size: 0.8rem;
      text-align: center;
    }
    .log-table tbody th {
      background: rgba(124, 77, 43, 0.05);
      font-weight: 700;
    }
    .log-table tbody tr:nth-child(even) td { background: rgba(255, 255, 255, 0.5); }
    .log-table tbody tr:nth-child(5n) th,
    .log-table tbody tr:nth-child(5n) td {
      border-bottom: 2px solid rgba(124, 77, 43, 0.45);
    }
    .log-table tr.located th,
    .log-table tr.located td { background: rgba(200, 154, 108, 0.28); }

    .book-controls {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }
    .book-controls .home-link { margin-right: auto; }
    .controls-spacer { margin-left: auto; width: 92px; }

    .jump-form { display: flex; align-items: center; gap: 6px; }
    .jump-form label {
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--muted);
    }
    .jump-form input {
      width: 96px;
      padding: 8px 10px;
      border: 1px solid var(--border);
      border-radius: 999px;
      background: #fff;
      color: var(--ink);
      font: inherit;
    }
    .jump-form input:focus { outline: 2px solid rgba(124, 77, 43, 0.25); outline-offset: 1px; }

    @media (max-width: 720px) {
      .book-spread.two { grid-template-columns: 1fr; }
      .book-spread.two .book-page { width: auto; max-width: 100%; }
      .book-spread.two::after { display: none; }
    }
"""

INDEX_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Napier Tables</title>
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
  <style>
{{ base_css }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <h1>Napier Tables</h1>
      <p class="lede">Create logarithm table configurations and read each one as a paginated book, one sheet or a two-page spread at a time.</p>
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
    <p>Open a table to read it page by page; edit and delete actions are inline.</p>
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
    <a class="link-button" href="/tables/{id}/read">Read</a>
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

BOOK_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Napier Tables · Reader</title>
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
  <style>
{{ base_css }}
{{ book_css }}
  </style>
</head>
<body>
  <main class="book-shell">
    <div class="zoom-bar" id="zoom-bar">
      <button class="link-button" id="zoom-out" type="button" aria-label="Zoom out">−</button>
      <span class="zoom-level" id="zoom-level">100%</span>
      <button class="link-button" id="zoom-in" type="button" aria-label="Zoom in">+</button>
      <button class="link-button" id="zoom-fit" type="button">Fit page</button>
    </div>
    {{ book|safe }}
  </main>
  <script>
    (function () {
      var MIN_ZOOM = 0.3;
      var MAX_ZOOM = 2.5;
      var zoom = 1;

      function spread() {
        return document.querySelector('.book-spread');
      }

      function apply() {
        var element = spread();
        if (!element) return;
        element.style.zoom = zoom;
        document.getElementById('zoom-level').textContent = Math.round(zoom * 100) + '%';
      }

      function fit() {
        var element = spread();
        if (!element) return;
        element.style.zoom = 1;
        var rect = element.getBoundingClientRect();
        var top = rect.top;
        var controls = document.querySelector('.book-controls');
        var chrome = (controls ? controls.offsetHeight : 0) + 56;
        var availableWidth = document.querySelector('.book-shell').clientWidth - 40;
        var availableHeight = Math.max(window.innerHeight - top - chrome, 140);
        zoom = Math.min(availableWidth / rect.width, availableHeight / rect.height, 1.5);
        zoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, zoom));
        apply();
      }

      function step(factor) {
        zoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, zoom * factor));
        apply();
      }

      document.getElementById('zoom-out').addEventListener('click', function () { step(1 / 1.2); });
      document.getElementById('zoom-in').addEventListener('click', function () { step(1.2); });
      document.getElementById('zoom-fit').addEventListener('click', fit);
      window.addEventListener('resize', fit);
      document.body.addEventListener('htmx:afterSwap', apply);
      fit();
    })();
  </script>
</body>
</html>
"""

BOOK_FRAGMENT_TEMPLATE = """<div id="book" class="book" data-table-id="{id}">
  <div class="book-toolbar">
    <div>
      <strong>Table {id}</strong>
      <span class="meta">Precision {precision} · Log precision {log_precision}</span>
    </div>
    <span class="meta">{pages_label}</span>
  </div>
  <div class="book-spread{spread_class}">
    {pages}
  </div>
  <div class="book-controls">
    <a class="link-button home-link" href="/">All tables</a>
    <button class="link-button" {back_disabled} hx-get="{back_url}" hx-target="#book" hx-swap="outerHTML" hx-push-url="true">◀ Back</button>
    <form class="jump-form" hx-get="{reader_url}" hx-target="#book" hx-swap="outerHTML" hx-push-url="true">
      <label for="jump-page-{id}">Page</label>
      <input id="jump-page-{id}" name="page" type="number" min="1" max="{total_pages}" placeholder="{page_placeholder}">
      <input type="hidden" name="spread" value="{spread_value}">
      <button class="link-button" type="submit">Go</button>
    </form>
    <form class="jump-form" hx-get="{reader_url}" hx-target="#book" hx-swap="outerHTML" hx-push-url="true">
      <label for="jump-value-{id}">Value</label>
      <input id="jump-value-{id}" name="value" type="text" inputmode="decimal" placeholder="{value_placeholder}">
      <input type="hidden" name="spread" value="{spread_value}">
      <button class="link-button" type="submit">Go</button>
    </form>
    <button class="link-button" hx-get="{toggle_url}" hx-target="#book" hx-swap="outerHTML" hx-push-url="true">{toggle_label}</button>
    <button class="link-button" {forward_disabled} hx-get="{forward_url}" hx-target="#book" hx-swap="outerHTML" hx-push-url="true">Forward ▶</button>
    <span class="controls-spacer"></span>
  </div>
</div>
"""

BOOK_PAGE_TEMPLATE = """<section class="book-page">
  <h3>Page {page} of {total}: {start} to {end}</h3>
  <p class="legend">Each entry gives the digits only — 3010 reads 0.3010.</p>
  <table class="log-table" style="--value-width: {value_width}ch; --n-width: {n_width}ch">
    <colgroup>
      <col class="col-n">
      {column_cols}
    </colgroup>
    <thead>
      <tr><th>N</th>{column_heads}</tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</section>"""


ROWS_PER_BOOK_PAGE = 20


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
    return render_template_string(
        INDEX_TEMPLATE, table_list=_render_table_list(rows), base_css=BASE_CSS
    )


def _book_page_count(precision: int) -> int:
    total_rows = 9 * 10 ** (precision - 1)
    return -(-total_rows // ROWS_PER_BOOK_PAGE)


def _locate_value(raw: str, precision: int) -> int:
    """Snap a decimal string such as ``"2.1212"`` onto the nearest table value."""
    try:
        value = Fraction(raw)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"invalid value: {raw!r}") from exc
    if value <= 0:
        raise ValueError(f"value must be positive: {raw!r}")

    scaled = round_ratio(value.numerator * 10**precision, value.denominator, 1)
    return min(max(scaled, 10**precision), 10 ** (precision + 1) - 1)


def _page_for_value(scaled_value: int, precision: int) -> int:
    row_index = (scaled_value - 10**precision) // 10
    return row_index // ROWS_PER_BOOK_PAGE + 1


def _render_book_page(
    spec: TableSpec, page_number: int, total_pages: int, highlight_row: int | None = None
) -> str:
    first_value = 10**spec.precision + (page_number - 1) * ROWS_PER_BOOK_PAGE * 10
    last_value = min(
        first_value + ROWS_PER_BOOK_PAGE * 10 - 1, 10 ** (spec.precision + 1) - 1
    )
    column_heads = "".join(f"<th>{column}</th>" for column in range(10))
    column_cols = '<col class="col-value">' * 10
    max_row_number = (10 ** (spec.precision + 1) - 1) // 10
    n_width = len(str(max_row_number)) + 1
    value_width = spec.log_precision + 1
    body_rows = []
    for row_start in range(first_value, last_value + 1, 10):
        row_number = row_start // 10
        if row_number % 5 == 0:
            row_header = str(row_number)
        else:
            row_header = str(row_number % 10)
        row_class = (
            ' class="located"'
            if highlight_row is not None and row_number == highlight_row
            else ""
        )
        cells = [f"<th>{row_header}</th>"]
        for column in range(10):
            scaled = log10_scaled(
                row_start + column, spec.precision, spec.log_precision
            )
            cells.append(f"<td>{scaled:0{spec.log_precision}d}</td>")
        body_rows.append(f"<tr{row_class}>" + "".join(cells) + "</tr>")
    return BOOK_PAGE_TEMPLATE.format(
        page=page_number,
        total=total_pages,
        start=scaled_to_text(first_value, spec.precision),
        end=scaled_to_text(last_value, spec.precision),
        value_width=value_width,
        n_width=n_width,
        column_cols=column_cols,
        column_heads=column_heads,
        rows="\n      ".join(body_rows),
    )


def _render_book(
    spec: TableSpec, page: int, spread: bool, highlight_value: int | None = None
) -> str:
    total_pages = _book_page_count(spec.precision)
    reader_url = f"/tables/{spec.id}/read"
    highlight_row = highlight_value // 10 if highlight_value is not None else None

    if spread:
        last_left = total_pages if total_pages % 2 == 1 else total_pages - 1
        page = min(max(page if page % 2 == 1 else page - 1, 1), max(last_left, 1))
        shown = [number for number in (page, page + 1) if number <= total_pages]
        back_page = max(1, page - 2)
        forward_page = min(page + 2, last_left)
        toggle_page = page
        toggle_spread = 0
        toggle_label = "One page"
        spread_class = " two"
    else:
        page = min(max(page, 1), total_pages)
        shown = [page]
        back_page = max(1, page - 1)
        forward_page = min(page + 1, total_pages)
        toggle_page = max(1, page if page % 2 == 1 else page - 1)
        toggle_spread = 1
        toggle_label = "Two pages"
        spread_class = ""

    pages_html = "\n".join(
        _render_book_page(spec, number, total_pages, highlight_row) for number in shown
    )
    if len(shown) > 1:
        pages_label = f"Pages {shown[0]}–{shown[-1]} of {total_pages}"
    else:
        pages_label = f"Page {shown[0]} of {total_pages}"

    first_shown_value = 10**spec.precision + (shown[0] - 1) * ROWS_PER_BOOK_PAGE * 10
    value_placeholder = scaled_to_text(first_shown_value, spec.precision)

    return BOOK_FRAGMENT_TEMPLATE.format(
        id=spec.id,
        precision=spec.precision,
        log_precision=spec.log_precision,
        pages_label=pages_label,
        pages=pages_html,
        spread_class=spread_class,
        reader_url=reader_url,
        total_pages=total_pages,
        page_placeholder=page,
        value_placeholder=value_placeholder,
        spread_value=int(spread),
        back_url=f"{reader_url}?page={back_page}&spread={int(spread)}",
        back_disabled="disabled" if back_page == page else "",
        forward_url=f"{reader_url}?page={forward_page}&spread={int(spread)}",
        forward_disabled="disabled" if forward_page == page else "",
        toggle_url=f"{reader_url}?page={toggle_page}&spread={toggle_spread}",
        toggle_label=toggle_label,
    )


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

    @app.get("/tables/<int:table_id>/read")
    def read_table(table_id: int) -> str:
        with get_session() as session:
            row = session.get(TableSpec, table_id)
        if row is None:
            abort(404)

        spread = request.args.get("spread", "0") == "1"
        try:
            page = int(request.args.get("page", "1"))
        except ValueError:
            abort(400)

        raw_value = request.args.get("value", "").strip()
        highlight_value = None
        if raw_value:
            try:
                highlight_value = _locate_value(raw_value, row.precision)
            except ValueError:
                abort(400)
            page = _page_for_value(highlight_value, row.precision)

        fragment = _render_book(row, page, spread, highlight_value)
        if _is_htmx_request():
            return fragment
        return render_template_string(
            BOOK_TEMPLATE,
            base_css=BASE_CSS,
            book_css=BOOK_CSS,
            book=fragment,
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
