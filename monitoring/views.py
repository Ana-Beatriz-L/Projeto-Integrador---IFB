"""Views (Pessoa 2). Finas: validam entrada, chamam services, montam a resposta."""
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    DISCLAIMER,  # noqa: F401
    ErrorResponseSerializer,
    SeriesResponseSerializer,
    StationListResponseSerializer,
    StationSummaryResponseSerializer,
)
from . import services  # noqa: F401


class StationListView(APIView):
    http_method_names = ["get"]

    @extend_schema(
        summary="Lista as estações",
        responses={200: StationListResponseSerializer},
    )
    def get(self, request):
        # TODO: services.list_stations() -> StationSerializer -> contrato 3.1
        raise NotImplementedError


class StationSummaryView(APIView):
    http_method_names = ["get"]

    @extend_schema(
        summary="Resumo da estação (últimas leituras)",
        responses={
            200: StationSummaryResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request, station_id):
        # TODO: contrato 3.2
        raise NotImplementedError


class StationSeriesView(APIView):
    http_method_names = ["get"]

    @extend_schema(
        summary="Série histórica de nível ou chuva",
        parameters=[
            OpenApiParameter("metric", str, enum=["level", "rain"], required=True),
            OpenApiParameter("hours", int, required=False, description="1 a 72 (padrão 24)"),
        ],
        responses={
            200: SeriesResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request, station_id):
        # TODO: contrato 3.3. Ordem: estacao (404) -> metric/hours (400).
        # Atencao: no JSON final os campos "from" e "to" (strings ISO UTC ou null)
        # sao montados no dict da resposta, nao no serializer.
        raise NotImplementedError
