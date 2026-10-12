"""Baixa apenas o CSV esperado da base pública do Kaggle."""
from pathlib import Path
from urllib.request import urlopen, Request
from zipfile import ZipFile
from io import BytesIO

URL = "https://www.kaggle.com/api/v1/datasets/download/atulanandjha/temperature-readings-iot-devices"
target = Path(__file__).resolve().parents[1] / "data/IOT-temp.csv"
target.parent.mkdir(exist_ok=True)
with urlopen(Request(URL, headers={"User-Agent": "iot-academic-project"}), timeout=120) as response:
    archive = ZipFile(BytesIO(response.read()))
    matches = [name for name in archive.namelist() if Path(name).name == "IOT-temp.csv"]
    if len(matches) != 1:
        raise RuntimeError("CSV não encontrado. Baixe manualmente pela página do Kaggle.")
    target.write_bytes(archive.read(matches[0]))
print(f"Base salva em {target}")
