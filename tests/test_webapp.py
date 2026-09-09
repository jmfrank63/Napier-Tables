import sqlite3

import pytest

from napier_tables.webapp import create_app


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "tables.sqlite3"
    return create_app(
        {
            "TESTING": True,
            "DATABASE_URL": f"sqlite+pysqlite:///{database_path}",
        }
    )


@pytest.fixture()
def client(app):
    return app.test_client()


def test_start_page_renders_htmx_form_and_empty_list(client):
    response = client.get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "htmx.org" in body
    assert 'name="precision"' in body
    assert 'name="log_precision"' in body
    assert "No tables have been created yet." in body
    assert "window.innerWidth > window.innerHeight" in body


def test_crud_round_trip_persists_records_in_sqlite(client, app):
    create_response = client.post(
        "/tables",
        data={"precision": "3", "log_precision": "5"},
        headers={"HX-Request": "true"},
    )

    assert create_response.status_code == 200
    body = create_response.get_data(as_text=True)
    assert "Precision 3" in body
    assert "Log precision 5" in body

    with sqlite3.connect(app.config["DATABASE_PATH"]) as connection:
        row = connection.execute(
            "select id, precision, log_precision from table_specs"
        ).fetchone()

    assert row[1:] == (3, 5)

    record_id = row[0]
    update_response = client.put(
        f"/tables/{record_id}",
        data={"precision": "4", "log_precision": "6"},
        headers={"HX-Request": "true"},
    )

    assert update_response.status_code == 200
    updated_body = update_response.get_data(as_text=True)
    assert "Precision 4" in updated_body
    assert "Log precision 6" in updated_body

    delete_response = client.delete(
        f"/tables/{record_id}",
        headers={"HX-Request": "true"},
    )

    assert delete_response.status_code == 200
    assert "No tables have been created yet." in delete_response.get_data(as_text=True)

    with sqlite3.connect(app.config["DATABASE_PATH"]) as connection:
        count = connection.execute("select count(*) from table_specs").fetchone()[0]

    assert count == 0


def test_invalid_input_is_rejected_before_database_access(client, app):
    response = client.post(
        "/tables",
        data={"precision": "1; drop table table_specs; --", "log_precision": "5"},
    )

    assert response.status_code == 400

    with sqlite3.connect(app.config["DATABASE_PATH"]) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "select name from sqlite_master where type='table'"
            )
        }

    assert "table_specs" in tables


def test_read_page_renders_first_book_page_with_log_values(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    response = client.get("/tables/1/read")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Page 1 of 5 · N 1.: 1.00 to 2.99" in body
    assert "0000" in body
    assert "0043" in body
    assert "3010" in body
    assert "◀ Back" in body
    assert "Forward ▶" in body
    assert "Two pages" in body


def test_read_page_clamps_out_of_range_pages_to_the_boundaries(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    second = client.get("/tables/1/read?page=2").get_data(as_text=True)
    assert "Page 2 of 5 · N 3.: 3.00 to 4.99" in second

    last = client.get("/tables/1/read?page=999").get_data(as_text=True)
    assert "Page 5 of 5 · N 9.: 9.00 to 9.99" in last

    first = client.get("/tables/1/read?page=0").get_data(as_text=True)
    assert "Page 1 of 5 · N 1.: 1.00 to 2.99" in first


def test_read_page_two_page_spread_shows_both_sheets(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    response = client.get("/tables/1/read?page=1&spread=1")

    body = response.get_data(as_text=True)
    assert "Pages 1–2 of 5" in body
    assert "Page 1 of 5 · N 1.: 1.00 to 2.99" in body
    assert "Page 2 of 5 · N 3.: 3.00 to 4.99" in body
    assert "One page" in body


def test_read_page_htmx_request_returns_fragment_only(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    response = client.get("/tables/1/read?page=1", headers={"HX-Request": "true"})

    body = response.get_data(as_text=True)
    assert "<!doctype html>" not in body.lower()
    assert 'id="book"' in body


def test_read_page_rejects_non_integer_page_number(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    assert client.get("/tables/1/read?page=oops").status_code == 400


def test_read_page_unknown_table_returns_404(client):
    assert client.get("/tables/7/read").status_code == 404


def test_table_list_links_to_the_reader(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    body = client.get("/").get_data(as_text=True)

    assert 'href="/tables/1/read"' in body


def test_reader_offers_page_and_value_jump_forms(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    body = client.get("/tables/1/read").get_data(as_text=True)

    assert 'name="page"' in body
    assert 'name="value"' in body
    assert "Go</button>" in body


def test_value_jump_lands_on_page_and_highlights_row(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    response = client.get("/tables/1/read?value=4.5")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Page 2 of 5 · N 3.: 3.00 to 4.99" in body
    assert '<tr class="located"><th>5</th>' in body
    assert "6532" in body


def test_value_jump_in_spread_mode_shows_odd_even_pair(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    body = client.get("/tables/1/read?value=5&spread=1").get_data(as_text=True)

    assert "Pages 3–4 of 5" in body
    assert "Page 3 of 5 · N 5.: 5.00 to 6.99" in body
    assert "Page 4 of 5 · N 7.: 7.00 to 8.99" in body
    assert '<tr class="located"><th>0</th>' in body


def test_value_jump_even_page_pairing_in_spread_mode(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    body = client.get("/tables/1/read?value=7&spread=1").get_data(as_text=True)

    assert "Pages 3–4 of 5" in body
    assert "Page 3 of 5 · N 5.: 5.00 to 6.99" in body
    assert "Page 4 of 5 · N 7.: 7.00 to 8.99" in body


def test_value_jump_clamps_out_of_range_values(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    below = client.get("/tables/1/read?value=0.25").get_data(as_text=True)
    assert "Page 1 of 5 · N 1.: 1.00 to 2.99" in below

    above = client.get("/tables/1/read?value=42").get_data(as_text=True)
    assert "Page 5 of 5 · N 9.: 9.00 to 9.99" in above


def test_value_jump_rejects_garbage_but_allows_empty(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    assert client.get("/tables/1/read?value=abc").status_code == 400
    assert client.get("/tables/1/read?value=2.5.3").status_code == 400
    assert client.get("/tables/1/read?value=").status_code == 200


def test_value_jump_respects_table_precision(client):
    client.post(
        "/tables",
        data={"precision": "4", "log_precision": "5"},
        headers={"HX-Request": "true"},
    )

    body = client.get("/tables/1/read?value=2.1212").get_data(as_text=True)

    assert "Page 57 of 450 · N 2.: 2.1200 to 2.1399" in body
    assert '<tr class="located"><th>121</th>' in body


def test_reader_page_starts_with_fit_to_viewport_zoom_controls(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    body = client.get("/tables/1/read").get_data(as_text=True)

    assert 'id="zoom-bar"' in body
    assert 'id="zoom-level"' in body
    assert "Fit page" in body
    assert "repeat(2, max-content)" in body
    assert "width: auto" in body
    assert "singleScale" in body
    assert "spreadScale" in body
    assert "window.innerWidth > window.innerHeight" in body


def test_entries_print_bare_mantissas_without_leading_zero(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    body = client.get("/tables/1/read").get_data(as_text=True)

    assert "Each entry gives the digits only" in body
    assert ">0000</td>" in body
    assert ">3010</td>" in body
    assert ">9996</td>" not in body


def test_row_labels_show_fraction_digits_only(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    body = client.get("/tables/1/read").get_data(as_text=True)

    assert "<th>0</th>" in body
    assert "<th>9</th>" in body
    assert "<th>10</th>" not in body
    assert "<th>11</th>" not in body
    assert "<th>15</th>" not in body
    assert "<th>16</th>" not in body


def test_table_columns_scale_with_digit_counts(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )
    client.post(
        "/tables",
        data={"precision": "9", "log_precision": "15"},
        headers={"HX-Request": "true"},
    )

    small = client.get("/tables/1/read").get_data(as_text=True)
    assert "--value-width: 5ch" in small
    assert "--n-width: 3ch" in small
    assert small.count('<col class="col-value">') == 10

    large = client.get("/tables/2/read").get_data(as_text=True)
    assert "--value-width: 16ch" in large
    assert "--n-width: 10ch" in large
    assert large.count('<col class="col-value">') == 10


def test_reader_layout_fills_viewport_without_scrolling(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    body = client.get("/tables/1/read").get_data(as_text=True)

    assert "overflow: hidden" in body
    assert "100vh" in body
    assert 'class="book-stage"' in body
    assert "availableSpace" in body


def test_rows_parameter_controls_rows_per_page(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    body = client.get("/tables/1/read?rows=30").get_data(as_text=True)

    assert "Page 1 of 3 · N 1.: 1.00 to 3.99" in body
    assert "<th>30</th>" in body
    assert 'data-rows="30"' in body
    assert 'data-first-value="100"' in body


def test_rows_parameter_is_clamped(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    wide = client.get("/tables/1/read?rows=5000").get_data(as_text=True)
    assert "Page 1 of 1 · N 1.: 1.00 to 9.99" in wide

    narrow = client.get("/tables/1/read?rows=1").get_data(as_text=True)
    assert "Page 1 of 18 · N 1.: 1.00 to 1.49" in narrow


def test_value_jump_respects_rows_parameter(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    body = client.get("/tables/1/read?value=4.5&rows=30").get_data(as_text=True)

    assert "Page 2 of 3 · N 4.: 4.00 to 6.99" in body
    assert '<tr class="located"><th>5</th>' in body


def test_invalid_rows_parameter_is_rejected(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    assert client.get("/tables/1/read?rows=oops").status_code == 400


def test_navigation_urls_carry_rows_parameter(client):
    client.post(
        "/tables",
        data={"precision": "2", "log_precision": "4"},
        headers={"HX-Request": "true"},
    )

    body = client.get("/tables/1/read?rows=30").get_data(as_text=True)

    assert "rows=30" in body
    assert 'name="rows"' in body
