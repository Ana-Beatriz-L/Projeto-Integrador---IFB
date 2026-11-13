"""Gera data/stations.csv e data/observations.csv.

Adaptacao do seed.js do desafio para Python puro (sem bibliotecas externas).

Uso:
    python scripts/generate_seed.py
    python scripts/generate_seed.py --end 2026-11-02T22:00:00Z   # fixa o ultimo horario

Igual ao seed.js original:
- 3 estacoes ficticias (EST-01, EST-02, EST-03)
- 73 horarios (de 72h atras ate a hora cheia atual), em UTC, ISO 8601 com "Z"
- 2 metricas por horario: level (m) e rain (mm/h)
- source = "synthetic"
"""
import argparse
import csv
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATIONS_CSV = DATA_DIR / "stations.csv"
OBSERVATIONS_CSV = DATA_DIR / "observations.csv"

STATIONS = [
    {"id": "EST-01", "name": "Estação Aurora", "river": "Rio Aurora", "municipality": "Vila Aurora"},
    {"id": "EST-02", "name": "Estação Vale Verde", "river": "Rio Verde", "municipality": "Vale Verde"},
    {"id": "EST-03", "name": "Estação Campo Alto", "river": "Rio do Campo", "municipality": "Campo Alto"},
]

STATION_COLUMNS = ["id", "name", "river", "municipality"]
OBSERVATION_COLUMNS = ["station_id", "metric", "observed_at", "value", "unit", "source"]


def iso_utc(dt):
    """Formato do contrato: 2026-11-02T10:00:00Z (o seed.js usa toISOString, com milissegundos)."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_end(raw):
    if raw is None:
        now = datetime.now(timezone.utc)
        return now.replace(minute=0, second=0, microsecond=0)
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)


def generate_rows(end_hour):
    rows = []
    for index in range(73):
        timestamp = iso_utc(end_hour - timedelta(hours=72 - index))
        for station_index, station in enumerate(STATIONS):
            level = 1.05 + station_index * 0.24 + 0.08 * math.sin(index / 5 + station_index)
            if (index + station_index * 7) % 17 < 3:
                rain = 0.4 + ((index + station_index) % 4) * 0.35
            else:
                rain = 0

            rows.append({
                "station_id": station["id"], "metric": "level", "observed_at": timestamp,
                "value": f"{level:.2f}", "unit": "m", "source": "synthetic",
            })
            rows.append({
                "station_id": station["id"], "metric": "rain", "observed_at": timestamp,
                "value": f"{rain:.2f}", "unit": "mm/h", "source": "synthetic",
            })
    return rows


def write_csv(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Gera os CSVs da amostra simulada.")
    parser.add_argument("--end", help="Ultimo horario (ISO 8601 UTC). Padrao: hora cheia atual.")
    args = parser.parse_args()

    rows = generate_rows(parse_end(args.end))
    write_csv(STATIONS_CSV, STATION_COLUMNS, STATIONS)
    write_csv(OBSERVATIONS_CSV, OBSERVATION_COLUMNS, rows)
    print(f"{len(STATIONS)} estações em {STATIONS_CSV}")
    print(f"{len(rows)} observações em {OBSERVATIONS_CSV}")


if __name__ == "__main__":
    main()
