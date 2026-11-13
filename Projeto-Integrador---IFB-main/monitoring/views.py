"""Views (Pessoa 2). Finas: validam entrada, chamam services, montam a resposta."""
from datetime import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import (
    DISCLAIMER,
    ErrorResponseSerializer,
    LatestReadingSerializer,
    SeriesPointSerializer,
    SeriesResponseSerializer,
    StationListResponseSerializer,
    StationSerializer,
    StationSummaryResponseSerializer,
)


def _format_iso_utc(dt):
    """Formata um datetime para string ISO 8601 UTC com sufixo 'Z'."""
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class StationListView(APIView):
    http_method_names = ["get"]

    @extend_schema(
        summary="Lista as estações",
        responses={200: StationListResponseSerializer},
    )
    def get(self, request):
        stations = services.list_stations()
        serializer = StationSerializer(stations, many=True)

        return Response(
            {
                "simulated": True,
                "disclaimer": DISCLAIMER,
                "count": len(serializer.data),
                "results": serializer.data,
            }
        )


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
        station = services.get_station_or_404(station_id)
        summary = services.get_summary(station)

        latest_level = summary["latest_level"]
        latest_rain = summary["latest_rain"]

        return Response(
            {
                "simulated": True,
                "disclaimer": DISCLAIMER,
                "station": StationSerializer(station).data,
                "latest_level": (
                    LatestReadingSerializer(latest_level).data
                    if latest_level
                    else None
                ),
                "latest_rain": (
                    LatestReadingSerializer(latest_rain).data
                    if latest_rain
                    else None
                ),
            }
        )


class StationSeriesView(APIView):
    http_method_names = ["get"]

    @extend_schema(
        summary="Série histórica de nível ou chuva",
        parameters=[
            OpenApiParameter("metric", str, enum=["level", "rain"], required=True),
            OpenApiParameter(
                "hours", int, required=False, description="1 a 72 (padrão 24)"
            ),
        ],
        responses={
            200: SeriesResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request, station_id):
        # Ordem do contrato: 1º valida estação (404), 2º valida query params (400)
        station = services.get_station_or_404(station_id)
        metric = services.parse_metric(request.query_params.get("metric"))
        hours = services.parse_hours(request.query_params.get("hours"))

        observations = list(services.get_series(station, metric, hours))
        points_data = SeriesPointSerializer(observations, many=True).data

        # Calcula o intervalo [from, to] caso existam observações na janela
        if observations:
            from_dt = _format_iso_utc(observations[0].observed_at)
            to_dt = _format_iso_utc(observations[-1].observed_at)
        else:
            from_dt = None
            to_dt = None

        return Response(
            {
                "simulated": True,
                "disclaimer": DISCLAIMER,
                "station_id": station.id,
                "metric": metric,
                "unit": services.METRICS[metric],
                "hours": hours,
                "from": from_dt,
                "to": to_dt,
                "count": len(points_data),
                "data": points_data,
            }
        )