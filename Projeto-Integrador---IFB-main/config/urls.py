from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/", include("monitoring.urls")),
]

# Erros 404/500 fora do DRF tambem seguem o contrato (JSON)
handler404 = "monitoring.exceptions.json_not_found"
handler500 = "monitoring.exceptions.json_server_error"
