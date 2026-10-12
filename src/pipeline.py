"""Ingestão transacional do CSV do Kaggle com validação e auditoria."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sqlalchemy import text
from src.database import get_engine

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = {"id": "reading_id", "room_id/id": "device_id", "noted_date": "observed_at",
           "temp": "temperature", "out/in": "location"}


def transform(raw):
    missing = set(COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {sorted(missing)}")
    df = raw[list(COLUMNS)].rename(columns=COLUMNS).copy()
    for column in ("reading_id", "device_id", "location"):
        df[column] = df[column].astype("string").str.strip().replace("", pd.NA)
    df["observed_at"] = pd.to_datetime(df.observed_at, format="%d-%m-%Y %H:%M", errors="coerce")
    df["temperature"] = pd.to_numeric(df.temperature, errors="coerce")
    valid = df.notna().all(axis=1) & np.isfinite(df.temperature) & df.location.isin(["In", "Out"])
    clean = df[valid].copy()
    # IDs repetidos com valores divergentes não podem ser escolhidos silenciosamente.
    if clean.drop_duplicates().reading_id.duplicated().any():
        raise ValueError("Há IDs repetidos com valores conflitantes no CSV.")
    duplicates = int(clean.reading_id.duplicated().sum())
    clean = clean.drop_duplicates("reading_id")
    audit = {"linhas_origem": len(raw), "linhas_invalidas": int((~valid).sum()),
             "ids_duplicados": duplicates, "linhas_validas": len(clean)}
    if clean.empty:
        raise ValueError("O arquivo não contém leituras válidas.")
    return clean, audit


def run(csv_path):
    df, audit = transform(pd.read_csv(csv_path))
    engine = get_engine()
    if engine.dialect.name != "postgresql":
        raise ValueError("O pipeline de entrega exige PostgreSQL.")
    with engine.begin() as conn:
        for statement in (ROOT / "sql/schema.sql").read_text().split(";"):
            if statement.strip():
                conn.execute(text(statement))
        # Serializa cargas; tabela temporária é exclusiva desta conexão.
        conn.execute(text("LOCK TABLE temperature_readings IN SHARE ROW EXCLUSIVE MODE"))
        conn.execute(text("CREATE TEMP TABLE staging (LIKE temperature_readings) ON COMMIT DROP"))
        df.to_sql("staging", conn, if_exists="append", index=False, chunksize=2000, method="multi")
        result = conn.execute(text("""INSERT INTO temperature_readings SELECT * FROM staging
            ON CONFLICT (reading_id) DO UPDATE SET device_id=EXCLUDED.device_id,
            observed_at=EXCLUDED.observed_at, temperature=EXCLUDED.temperature,
            location=EXCLUDED.location"""))
        audit["linhas_processadas_banco"] = result.rowcount
        for statement in (ROOT / "sql/views.sql").read_text().split(";"):
            if statement.strip():
                conn.execute(text(statement))
        audit["total_banco"] = conn.scalar(text("SELECT COUNT(*) FROM temperature_readings"))
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/qualidade.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit, indent=2))
    return audit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default="data/IOT-temp.csv")
    run(parser.parse_args().csv)
