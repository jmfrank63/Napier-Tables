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
