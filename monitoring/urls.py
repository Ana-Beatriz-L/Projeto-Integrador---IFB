from django.urls import path

from . import views

urlpatterns = [
    path("stations", views.StationListView.as_view(), name="station-list"),
    path(
        "stations/<str:station_id>/summary",
        views.StationSummaryView.as_view(),
        name="station-summary",
    ),
    path(
        "stations/<str:station_id>/series",
        views.StationSeriesView.as_view(),
        name="station-series",
    ),
]
