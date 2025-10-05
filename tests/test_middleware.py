from unittest.mock import Mock

from django.test import RequestFactory

from django_coralogix_otel.middleware import TraceMiddleware


class TestTraceMiddleware:
    """Testes para o TraceMiddleware"""

    def test_middleware_init(self):
        """Testa inicialização do middleware"""
        get_response = Mock()
        middleware = TraceMiddleware(get_response)
        assert middleware is not None
        assert middleware.get_response == get_response

    def test_middleware_call(self):
        """Testa processamento de requisição e resposta"""
        get_response = Mock(return_value=Mock(status_code=200))
        middleware = TraceMiddleware(get_response)
        factory = RequestFactory()
        request = factory.get("/")

        # Deve processar sem erros
        result = middleware(request)
        assert result is not None
        assert result.status_code == 200
        get_response.assert_called_once_with(request)

    def test_get_client_ip(self):
        """Testa obtenção de IP do cliente"""
        get_response = Mock()
        middleware = TraceMiddleware(get_response)
        factory = RequestFactory()

        # Test com IP normal
        request = factory.get("/", REMOTE_ADDR="192.168.1.1")
        assert middleware.get_client_ip(request) == "192.168.1.1"

        # Test com X-Forwarded-For
        request = factory.get("/", HTTP_X_FORWARDED_FOR="10.0.0.1, 192.168.1.1")
        assert middleware.get_client_ip(request) == "10.0.0.1"
