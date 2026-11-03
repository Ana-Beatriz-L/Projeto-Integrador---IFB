"""Testes (Pessoa 3). Rodar com: python manage.py test"""
import importlib.util
import tempfile
import unittest
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from monitoring.models import Observation, Station

_spec = importlib.util.spec_from_file_location(
    "generate_seed", Path(settings.BASE_DIR) / "scripts" / "generate_seed.py"
)
seed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(seed)


class BaseApiTest(TestCase):
    def setUp(self):
        self.station = Station.objects.create(
            id="EST-01", name="Estação Teste", river="Rio Teste",
            municipality="Município Teste",
        )
        at = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)
        Observation.objects.create(
            station=self.station, metric="level", observed_at=at, value="2.35", unit="m"
        )
        Observation.objects.create(
            station=self.station, metric="rain", observed_at=at, value="1.20", unit="mm/h"
        )


class ErrorFormatTests(BaseApiTest):
    def test_rota_inexistente_segue_contrato(self):
        resp = self.client.get("/api/nao-existe")
        self.assertEqual(resp.status_code, 404)
        body = resp.json()
        self.assertTrue(body["simulated"])
        self.assertEqual(body["error"], "not_found")


class StationEndpointTests(BaseApiTest):
    @unittest.skip("TODO: implementar GET /api/stations")
    def test_lista_estacoes(self):
        resp = self.client.get("/api/stations")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["simulated"])

    @unittest.skip("TODO: implementar summary")
    def test_summary_estacao_inexistente(self):
        resp = self.client.get("/api/stations/9999/summary")
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()["error"], "station_not_found")

    @unittest.skip("TODO: implementar series")
    def test_series_metrica_invalida(self):
        resp = self.client.get(f"/api/stations/{self.station.id}/series?metric=foo")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["error"], "invalid_metric")

    @unittest.skip("TODO: implementar series")
    def test_series_hours_fora_do_intervalo(self):
        resp = self.client.get(
            f"/api/stations/{self.station.id}/series?metric=level&hours=100"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["error"], "invalid_hours")


class SeedTests(TestCase):
    def test_import_repetivel(self):
        """Rodar a importacao duas vezes nao duplica linhas."""
        with tempfile.TemporaryDirectory() as tmp:
            stations, observations = Path(tmp) / "s.csv", Path(tmp) / "o.csv"
            seed.write_csv(stations, seed.STATION_COLUMNS, seed.STATIONS)
            end = seed.parse_end("2026-11-02T10:00:00Z")
            seed.write_csv(observations, seed.OBSERVATION_COLUMNS, seed.generate_rows(end))

            args = ["--stations", str(stations), "--observations", str(observations)]
            call_command("import_observations", *args, stdout=StringIO())
            first = Observation.objects.count()
            call_command("import_observations", *args, stdout=StringIO())

        self.assertEqual(first, 3 * 2 * 73)  # 3 estacoes x 2 metricas x 73 horarios
        self.assertEqual(Observation.objects.count(), first)
        self.assertEqual(Station.objects.count(), 3)
