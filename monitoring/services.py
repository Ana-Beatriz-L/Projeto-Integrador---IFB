"""Regras de negocio e consultas (Pessoa 2).

As views chamam estas funcoes; elas levantam os erros de monitoring/exceptions.py.
Use o ORM do Django (consultas parametrizadas) e siga docs/api-contract.md.
"""
from .exceptions import InvalidHours, InvalidMetric, StationNotFound  # noqa: F401
from .models import Observation, Station  # noqa: F401

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
    # TODO
    raise NotImplementedError


def get_station_or_404(station_id):
    """Busca a estacao pelo id (texto, ex: EST-01). Inexistente -> StationNotFound."""
    # TODO
    raise NotImplementedError


def get_summary(station):
    """Retorna a ultima leitura de nivel e a ultima de chuva (ou None se nao houver)."""
    # TODO
    raise NotImplementedError


def parse_metric(raw):
    """Valida 'metric' (obrigatorio: level|rain). Invalido -> InvalidMetric."""
    # TODO
    raise NotImplementedError


def parse_hours(raw):
    """Valida 'hours' (inteiro 1..72, padrao 24). Invalido -> InvalidHours."""
    # TODO
    raise NotImplementedError


def get_series(station, metric, hours):
    """Leituras da janela que termina na ultima observacao da estacao.

    - filtrar Observation por station e metric; janela de [ultima - hours, ultima]
    - ordenar por observed_at crescente
    - horarios sem leitura simplesmente nao aparecem (lacunas)
    - serie vazia nao e erro
    """
    # TODO
    raise NotImplementedError
