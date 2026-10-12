"""Valida a carga real, a repetição idempotente e a consistência das views."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import text
from src.database import get_engine
from src.pipeline import run

first = run("data/IOT-temp.csv")
second = run("data/IOT-temp.csv")
assert first["total_banco"] == second["total_banco"] == 97605
with get_engine().connect() as conn:
    avg = conn.execute(text("SELECT SUM(leituras) FROM avg_temp_por_dispositivo")).scalar()
    hourly = conn.execute(text("SELECT SUM(contagem) FROM leituras_por_hora")).scalar()
    invalid = conn.execute(text("SELECT COUNT(*) FROM temp_max_min_por_dia WHERE temp_min > temp_max")).scalar()
    assert avg == hourly == 97605
    assert invalid == 0
Path("docs/integracao.json").write_text(json.dumps({
    "banco": "PostgreSQL", "total": second["total_banco"], "reexecucao_sem_duplicacao": True,
    "soma_views_confere": True, "minimos_maximos_consistentes": True
}, indent=2), encoding="utf-8")
print("Integração PostgreSQL e idempotência: OK")
