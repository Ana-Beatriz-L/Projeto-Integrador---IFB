"""Regras de negocio e consultas (Pessoa 2).

As views chamam estas funcoes; elas levantam os erros de monitoring/exceptions.py.
Use o ORM do Django (consultas parametrizadas) e siga docs/api-contract.md.
"""
from datetime import timedelta

from .exceptions import InvalidHours, InvalidMetric, StationNotFound
from .models import Observation, Station

METRICS = {
    # metric -> unidade (a metrica e uma coluna de Observation, como no seed.js)
    "level": "m",
    "rain": "mm/h",
}
DEFAULT_HOURS = 24
MIN_HOURS = 1
MAX_HOURS = 72


def list_stations():
    """Retorna as estacoes ordenadas por id."""
    return Station.objects.all().order_by("id")


def get_station_or_404(station_id):
    """Busca a estacao pelo id (texto, ex: EST-01). Inexistente -> StationNotFound."""
    try:
        return Station.objects.get(id=station_id)
    except Station.DoesNotExist:
        raise StationNotFound()


def get_summary(station):
    """Retorna a ultima leitura de nivel e a ultima de chuva (ou None se nao houver)."""
    latest_level = (
        Observation.objects.filter(
            station=station, metric=Observation.Metric.LEVEL
        )
        .order_by("observed_at")
        .last()
    )
    latest_rain = (
        Observation.objects.filter(
            station=station, metric=Observation.Metric.RAIN
        )
        .order_by("observed_at")
        .last()
    )
    return {
        "latest_level": latest_level,
        "latest_rain": latest_rain,
    }


def parse_metric(raw):
    """Valida 'metric' (obrigatorio: level|rain). Invalido -> InvalidMetric."""
    if not raw or raw not in METRICS:
        raise InvalidMetric()
    return raw


def parse_hours(raw):
    """Valida 'hours' (inteiro 1..72, padrao 24). Invalido -> InvalidHours."""
    if raw is None or raw == "":
        return DEFAULT_HOURS

    # Evita que booleanos passem no isinstance/int em chamadas diretas em Python
    if isinstance(raw, bool):
        raise InvalidHours()

    try:
        hours = int(raw)
    except (ValueError, TypeError):
        raise InvalidHours()

    if not (MIN_HOURS <= hours <= MAX_HOURS):
        raise InvalidHours()

    return hours


def get_series(station, metric, hours):
    """Leituras da janela que termina na ultima observacao da estacao.

    - filtrar Observation por station e metric; janela de [ultima - hours, ultima]
    - ordenar por observed_at crescente
    - horarios sem leitura simplesmente nao aparecem (lacunas)
    - serie vazia nao e erro
    """
    base_qs = Observation.objects.filter(station=station, metric=metric).order_by(
        "observed_at"
    )
    latest_obs = base_qs.last()

    # Se não houver observações para a estação/métrica, retorna queryset vazio
    if not latest_obs:
        return base_qs.none()

    end_time = latest_obs.observed_at
    start_time = end_time - timedelta(hours=hours)

    return base_qs.filter(
        observed_at__gte=start_time,
        observed_at__lte=end_time,
    ).order_by("observed_at")