import sqlite3

import pytest

from napier_tables.webapp import create_app


SPEC_FORM = {
    "precision": "3",
    "log_precision": "5",
    "base": "10",
    "start": "1",
    "end": "20",
}


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
    assert 'name="base"' in body
    assert 'name="start"' in body
    assert 'name="end"' in body
    assert "No tables have been created yet." in body


def test_crud_round_trip_persists_records_in_sqlite(client, app):
    create_response = client.post(
        "/tables",
        data=SPEC_FORM,
        headers={"HX-Request": "true"},
    )

    assert create_response.status_code == 200
    body = create_response.get_data(as_text=True)
    assert "Base 10" in body
    assert "Log precision 5" in body

    with sqlite3.connect(app.config["DATABASE_PATH"]) as connection:
        row = connection.execute(
            "select id, precision, log_precision, base, start, end from table_specs"
        ).fetchone()

    assert row[1:] == (3, 5, 10, 1, 20)

    record_id = row[0]
    update_response = client.put(
        f"/tables/{record_id}",
        data={**SPEC_FORM, "log_precision": "6", "base": "2", "end": "8"},
        headers={"HX-Request": "true"},
    )

    assert update_response.status_code == 200
    updated_body = update_response.get_data(as_text=True)
    assert "Base 2" in updated_body
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
        data={**SPEC_FORM, "precision": "1; drop table table_specs; --"},
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


def _create_spec(client, **overrides):
    response = client.post(
        "/tables",
        data={**SPEC_FORM, **overrides},
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    return 1


def test_start_page_shows_an_empty_table_view_placeholder(client):
    body = client.get("/").get_data(as_text=True)

    assert 'id="table-view"' in body
    assert "No table is being shown yet." in body


def test_saved_row_offers_a_show_table_action(client):
    _create_spec(client)

    body = client.get("/").get_data(as_text=True)

    assert "Show table" in body
    assert 'hx-get="/tables/1/table"' in body


def test_show_table_renders_generated_rows(client):
    _create_spec(client, base="10", start="1", end="10", log_precision="4")

    response = client.get("/tables/1/table", headers={"HX-Request": "true"})

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "0.0000" in body  # log10(1)
    assert "0.3010" in body  # log10(2)
    assert "0.4771" in body  # log10(3)
    assert "1.0000" in body  # log10(10)
    assert body.count("<tr>") == 11  # header row plus ten value rows


def test_show_table_respects_base_and_precision(client):
    _create_spec(client, base="2", start="1", end="8", log_precision="3")

    body = client.get(
        "/tables/1/table", headers={"HX-Request": "true"}
    ).get_data(as_text=True)

    assert "3.000" in body  # log2(8)
    assert "log<sub>2</sub> N" in body


def test_show_table_without_htmx_returns_the_whole_page(client):
    _create_spec(client, start="1", end="5")

    body = client.get("/tables/1/table").get_data(as_text=True)

    assert "htmx.org" in body
    assert 'id="table-list"' in body
    assert 'class="log-table"' in body


def test_show_table_refuses_ranges_beyond_the_row_limit(client):
    _create_spec(client, start="1", end="99999")

    body = client.get(
        "/tables/1/table", headers={"HX-Request": "true"}
    ).get_data(as_text=True)

    assert "narrow the input range" in body
    assert "log-table" not in body


def test_show_table_returns_404_for_a_missing_record(client):
    assert client.get("/tables/999/table").status_code == 404


def test_create_rejects_an_end_below_start(client):
    response = client.post("/tables", data={**SPEC_FORM, "start": "10", "end": "5"})

    assert response.status_code == 400


def test_create_rejects_a_base_below_two(client):
    response = client.post("/tables", data={**SPEC_FORM, "base": "1"})

    assert response.status_code == 400
