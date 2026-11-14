"""Serializers (Pessoa 2) e descricao das respostas para o Swagger (Pessoa 3).

Os formatos seguem docs/api-contract.md.
"""
from rest_framework import serializers

from .models import Station

DISCLAIMER = (
    "Dados simulados para fins didáticos. "
    "Não representam rios reais nem devem embasar alertas ou decisões."
)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ["id", "name", "river", "municipality"]


class StationListResponseSerializer(serializers.Serializer):
    simulated = serializers.BooleanField()
    disclaimer = serializers.CharField()
    count = serializers.IntegerField()
    results = StationSerializer(many=True)


class LatestReadingSerializer(serializers.Serializer):
    value = serializers.FloatField()
    unit = serializers.CharField()
    observed_at = serializers.DateTimeField()


class StationSummaryResponseSerializer(serializers.Serializer):
    simulated = serializers.BooleanField()
    disclaimer = serializers.CharField()
    station = StationSerializer()
    latest_level = LatestReadingSerializer(allow_null=True)
    latest_rain = LatestReadingSerializer(allow_null=True)


class SeriesPointSerializer(serializers.Serializer):
    observed_at = serializers.DateTimeField()
    value = serializers.FloatField()


class SeriesResponseSerializer(serializers.Serializer):
    simulated = serializers.BooleanField()
    disclaimer = serializers.CharField()
    station_id = serializers.CharField()
    metric = serializers.ChoiceField(choices=["level", "rain"])
    unit = serializers.CharField()
    hours = serializers.IntegerField()
    # from/to: "from" e palavra reservada do Python, ver nota na view
    count = serializers.IntegerField()
    data = SeriesPointSerializer(many=True)


class ErrorResponseSerializer(serializers.Serializer):
    simulated = serializers.BooleanField()
    error = serializers.CharField()
    message = serializers.CharField()
