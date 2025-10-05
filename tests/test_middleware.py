from unittest.mock import Mock

import pytest
from django.test import RequestFactory

from django_coralogix_otel.middleware import TraceMiddleware


class TestTraceMiddleware:
    """Testes para o TraceMiddleware"""

    def test_middleware_init(self):
        """Testa inicialização do middleware"""
        middleware = TraceMiddleware()
        assert middleware is not None

    def test_middleware_process_request(self):
        """Testa processamento de requisição"""
        middleware = TraceMiddleware()
        factory = RequestFactory()
        request = factory.get("/")

        # Deve processar sem erros
        result = middleware.process_request(request)
        assert result is None  # Middleware não deve retornar nada

    def test_middleware_process_response(self):
        """Testa processamento de resposta"""
        middleware = TraceMiddleware()
        factory = RequestFactory()
        request = factory.get("/")
        response = Mock()

        # Deve processar sem erros
        result = middleware.process_response(request, response)
        assert result == response  # Deve retornar a mesma resposta
