"""Importa data/stations.csv e data/observations.csv para o banco (Pessoa 1).

Uso: python manage.py import_observations
     python manage.py import_observations --stations X.csv --observations Y.csv

Repetivel: rodar duas vezes nao duplica linhas (mesma ideia do INSERT OR IGNORE do seed.js).
"""
import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from monitoring.models import Observation, Station

DATA_DIR = Path(settings.BASE_DIR) / "data"
BATCH_SIZE = 500


def parse_iso_utc(raw):
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


class Command(BaseCommand):
    help = "Importa estações e observações sintéticas a partir de CSV."

    def add_arguments(self, parser):
        parser.add_argument("--stations", default=str(DATA_DIR / "stations.csv"))
        parser.add_argument("--observations", default=str(DATA_DIR / "observations.csv"))

    @transaction.atomic
    def handle(self, *args, **options):
        stations_path = Path(options["stations"])
        observations_path = Path(options["observations"])
        for path in (stations_path, observations_path):
            if not path.exists():
                raise CommandError(
                    f"Arquivo não encontrado: {path}. Rode: python scripts/generate_seed.py"
                )

        with stations_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                Station.objects.update_or_create(
                    id=row["id"],
                    defaults={
                        "name": row["name"],
                        "river": row["river"],
                        "municipality": row["municipality"],
                    },
                )

        before = Observation.objects.count()
        batch = []
        with observations_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                batch.append(
                    Observation(
                        station_id=row["station_id"],
                        metric=row["metric"],
                        observed_at=parse_iso_utc(row["observed_at"]),
                        value=Decimal(row["value"]),
                        unit=row["unit"],
                        source=row["source"],
                    )
                )
                if len(batch) >= BATCH_SIZE:
                    Observation.objects.bulk_create(batch, ignore_conflicts=True)
                    batch = []
        if batch:
            Observation.objects.bulk_create(batch, ignore_conflicts=True)

        added = Observation.objects.count() - before
        self.stdout.write(
            self.style.SUCCESS(
                f"{Station.objects.count()} estações; {added} observações novas "
                f"({Observation.objects.count()} no total)."
            )
        )
