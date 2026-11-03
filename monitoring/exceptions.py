"""Erros no formato do contrato (docs/api-contract.md, secao 4).

Todo erro sai como: {"simulated": true, "error": "<codigo>", "message": "<texto>"}
"""
from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import APIException, MethodNotAllowed, NotFound
from rest_framework.response import Response


def error_body(code, message):
    return {"simulated": True, "error": code, "message": message}


class ApiError(APIException):
    """Erro de negocio com codigo proprio."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "bad_request"
    message = "Requisicao invalida."

    def __init__(self, message=None):
        super().__init__(detail=message or self.message)
        self.message = message or self.message


class StationNotFound(ApiError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "station_not_found"
    message = "Estação não encontrada."


class InvalidMetric(ApiError):
    code = "invalid_metric"
    message = "O parâmetro 'metric' é obrigatório e deve ser 'level' ou 'rain'."


class InvalidHours(ApiError):
    code = "invalid_hours"
    message = "O parâmetro 'hours' deve ser um inteiro entre 1 e 72."


def api_exception_handler(exc, context):
    """Handler do DRF: converte excecoes para o formato do contrato."""
    if isinstance(exc, ApiError):
        return Response(error_body(exc.code, exc.message), status=exc.status_code)
    if isinstance(exc, NotFound):
        return Response(error_body("not_found", "Rota não encontrada."), status=404)
    if isinstance(exc, MethodNotAllowed):
        return Response(
            error_body(
                "method_not_allowed",
                "Método não permitido. Esta API aceita apenas GET.",
            ),
            status=405,
        )
    # Qualquer outra coisa (inclusive bugs): 500 no formato do contrato.
    # TODO (Pessoa 3): decidir se vale logar o erro original aqui.
    return Response(
        error_body("internal_error", "Erro interno do servidor."), status=500
    )


def json_not_found(request, exception=None):
    return JsonResponse(error_body("not_found", "Rota não encontrada."), status=404)


def json_server_error(request):
    return JsonResponse(
        error_body("internal_error", "Erro interno do servidor."), status=500
    )
