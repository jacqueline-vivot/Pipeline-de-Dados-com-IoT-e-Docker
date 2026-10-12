import pandas as pd
import pytest
from src.pipeline import transform


def sample():
    return pd.DataFrame({"id": ["a", "b"], "room_id/id": ["Room Admin"]*2,
        "noted_date": ["08-12-2018 09:30", "01-11-2018 13:00"],
        "temp": [29, 41], "out/in": ["In", "Out"]})


def test_dates_are_day_first():
    clean, audit = transform(sample())
    assert clean.observed_at.iloc[0] == pd.Timestamp("2018-12-08 09:30")
    assert audit["linhas_validas"] == 2


def test_invalid_and_duplicate_rows():
    raw = sample()
    bad = raw.iloc[[0]].copy()
    bad["temp"] = float("inf")
    clean, audit = transform(pd.concat([raw, raw.iloc[[0]], bad]))
    assert len(clean) == 2
    assert audit["linhas_invalidas"] == 1
    assert audit["ids_duplicados"] == 1


def test_conflicting_ids_rejected():
    raw = sample()
    raw.loc[1, "id"] = "a"
    with pytest.raises(ValueError, match="conflitantes"):
        transform(raw)


def test_missing_column_rejected():
    with pytest.raises(ValueError, match="ausentes"):
        transform(sample().drop(columns="temp"))


@pytest.mark.parametrize("column,value", [
    ("id", "  "), ("room_id/id", None), ("noted_date", "31-02-2018 12:00"),
    ("temp", "texto"), ("temp", float("-inf")), ("out/in", "Unknown"),
])
def test_invalid_rows_are_counted(column, value):
    raw = sample().astype(object)
    raw.loc[0, column] = value
    clean, audit = transform(raw)
    assert clean.reading_id.tolist() == ["b"]
    assert audit["linhas_invalidas"] == 1


def test_blank_dataset_rejected():
    with pytest.raises(ValueError, match="leituras válidas"):
        transform(sample().iloc[:0])


def test_trims_identifiers_preserves_distinct_readings():
    raw = sample()
    raw.loc[0, "id"] = " a "
    raw.loc[0, "out/in"] = " In "
    raw.loc[1, "noted_date"] = raw.loc[0, "noted_date"]
    clean, audit = transform(raw)
    assert clean.reading_id.tolist() == ["a", "b"]
    assert clean.location.tolist() == ["In", "Out"]
    assert audit["linhas_validas"] == 2
