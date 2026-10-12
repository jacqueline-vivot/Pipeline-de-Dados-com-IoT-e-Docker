"""Integração opcional: TEST_DATABASE_URL deve apontar a PostgreSQL de teste.

Cada teste usa schema temporário próprio; não altera os dados do dashboard.
"""
import os
import shutil
import uuid
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from streamlit.testing.v1 import AppTest
import src.pipeline as pipeline
import src.database as database

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="PostgreSQL de teste não configurado")


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    schema = "test_" + uuid.uuid4().hex
    admin = create_engine(os.environ["TEST_DATABASE_URL"])
    with admin.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_engine(os.environ["TEST_DATABASE_URL"], connect_args={"options": f"-csearch_path={schema}"})
    shutil.copytree(ROOT / "sql", tmp_path / "sql")
    monkeypatch.setattr(pipeline, "ROOT", tmp_path)
    monkeypatch.setattr(pipeline, "get_engine", lambda: engine)
    monkeypatch.setattr(database, "get_engine", lambda: engine)
    try:
        yield engine, tmp_path
    finally:
        import streamlit as st
        st.cache_data.clear()
        engine.dispose()
        with admin.begin() as conn:
            conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


def write_sample(path, temp=29):
    frame = pd.DataFrame({"id": ["a", "b"], "room_id/id": ["Room Admin"] * 2,
        "noted_date": ["08-12-2018 09:30", "08-12-2018 13:00"],
        "temp": [temp, 41], "out/in": ["In", "Out"]})
    frame.to_csv(path, index=False)
    return path


def test_upsert_updates_without_duplicating(isolated_db):
    engine, tmp = isolated_db
    csv = write_sample(tmp / "sample.csv")
    assert pipeline.run(csv)["total_banco"] == 2
    write_sample(csv, temp=33)
    assert pipeline.run(csv)["total_banco"] == 2
    with engine.connect() as conn:
        assert conn.scalar(text("SELECT temperature FROM temperature_readings WHERE reading_id='a'")) == 33


def test_failed_sql_rolls_back_entire_load(isolated_db):
    engine, tmp = isolated_db
    csv = write_sample(tmp / "sample.csv")
    pipeline.run(csv)
    write_sample(csv, temp=99)
    (tmp / "sql/views.sql").write_text("SELECT missing_column FROM temperature_readings;")
    with pytest.raises(Exception):
        pipeline.run(csv)
    with engine.connect() as conn:
        assert conn.scalar(text("SELECT temperature FROM temperature_readings WHERE reading_id='a'")) == 29


def test_real_csv_views_match_independent_pandas_aggregations(isolated_db):
    engine, _ = isolated_db
    clean, audit = pipeline.transform(pd.read_csv(ROOT / "data/IOT-temp.csv"))
    first = pipeline.run(ROOT / "data/IOT-temp.csv")
    second = pipeline.run(ROOT / "data/IOT-temp.csv")
    assert first["total_banco"] == second["total_banco"] == len(clean) == 97605
    assert audit["ids_duplicados"] == 1
    expected_avg = clean.groupby(["device_id", "location"]).temperature.agg(leituras="count", avg_temp="mean").reset_index()
    expected_hour = clean.assign(hora=clean.observed_at.dt.hour).groupby(["hora", "location"]).size().reset_index(name="contagem")
    expected_day = clean.assign(data=clean.observed_at.dt.date).groupby(["data", "location"]).temperature.agg(temp_max="max", temp_min="min", temp_media="mean").reset_index()
    with engine.connect() as conn:
        for view, expected, keys in [
            ("avg_temp_por_dispositivo", expected_avg, ["device_id", "location"]),
            ("leituras_por_hora", expected_hour, ["hora", "location"]),
            ("temp_max_min_por_dia", expected_day, ["data", "location"]),
        ]:
            actual = pd.read_sql(text(f"SELECT * FROM {view}"), conn)
            pd.testing.assert_frame_equal(actual[expected.columns].sort_values(keys).reset_index(drop=True),
                expected.sort_values(keys).reset_index(drop=True), check_dtype=False, rtol=1e-10)


def test_dashboard_filters_and_empty_selection(isolated_db):
    _, tmp = isolated_db
    pipeline.run(write_sample(tmp / "sample.csv"))
    app = AppTest.from_file(str(ROOT / "src/dashboard.py"), default_timeout=30).run()
    assert not app.exception
    assert len(app.get("plotly_chart")) == 3
    assert app.metric[0].value == "2"
    app.multiselect[0].set_value(["In"]).run()
    assert not app.exception
    assert app.metric[0].value == "1"
    assert app.metric[1].value == "29.0 °C"
    app.multiselect[0].set_value([]).run()
    assert not app.exception
    assert "Selecione" in app.info[0].value
    app.multiselect[0].set_value(["Out"]).run()
    assert app.metric[1].value == "41.0 °C"
    app.button[0].click().run()
    assert not app.exception


def test_dashboard_handles_database_failure(isolated_db, monkeypatch):
    def unavailable():
        raise ConnectionError("falha simulada")
    monkeypatch.setattr(database, "get_engine", unavailable)
    app = AppTest.from_file(str(ROOT / "src/dashboard.py"), default_timeout=30).run()
    assert not app.exception
    assert "Não foi possível" in app.error[0].value


def test_dashboard_handles_empty_database(isolated_db):
    engine, tmp = isolated_db
    pipeline.run(write_sample(tmp / "sample.csv"))
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM temperature_readings"))
    app = AppTest.from_file(str(ROOT / "src/dashboard.py"), default_timeout=30).run()
    assert not app.exception
    assert "Nenhuma leitura" in app.info[0].value
