
from django.db import models


class Station(models.Model):
    id = models.CharField(max_length=20, primary_key=True)  # ex: EST-01
    name = models.CharField(max_length=120)
    river = models.CharField(max_length=120)
    municipality = models.CharField(max_length=120)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.id} - {self.name}"


class Observation(models.Model):
    class Metric(models.TextChoices):
        LEVEL = "level", "Nível (m)"
        RAIN = "rain", "Chuva (mm/h)"

    station = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="observations"
    )
    metric = models.CharField(max_length=10, choices=Metric.choices)
    observed_at = models.DateTimeField()  # UTC
    value = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=10)  # "m" ou "mm/h"
    source = models.CharField(max_length=20, default="synthetic")

    class Meta:
        ordering = ["observed_at"]
        constraints = [
            # Rodar o seed de novo nao duplica leituras (igual ao INSERT OR IGNORE)
            models.UniqueConstraint(
                fields=["station", "metric", "observed_at"],
                name="unique_station_metric_observed_at",
            )
        ]
        indexes = [models.Index(fields=["station", "metric", "observed_at"])]

    def __str__(self):
        return f"{self.station_id} {self.metric} @ {self.observed_at:%Y-%m-%dT%H:%M:%SZ}"
