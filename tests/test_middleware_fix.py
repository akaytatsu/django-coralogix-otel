from unittest.mock import Mock, patch

import pytest
from django.test import RequestFactory, TestCase

from django_coralogix_otel.middleware import OpenTelemetryMiddleware, _safe_set_attribute


class TestMiddlewareFixes(TestCase):
    """Testa as correções do middleware OpenTelemetry."""

    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = Mock(return_value=Mock(status_code=200))

    def test_safe_set_attribute_with_valid_types(self):
        """Testa _safe_set_attribute com tipos válidos."""
        mock_span = Mock()

        # Tipos válidos
        _safe_set_attribute(mock_span, "str_attr", "test")
        _safe_set_attribute(mock_span, "int_attr", 42)
        _safe_set_attribute(mock_span, "float_attr", 3.14)
        _safe_set_attribute(mock_span, "bool_attr", True)
        _safe_set_attribute(mock_span, "none_attr", None)

        # Verificar chamadas
        assert mock_span.set_attribute.call_count == 5
        mock_span.set_attribute.assert_any_call("str_attr", "test")
        mock_span.set_attribute.assert_any_call("int_attr", 42)

    def test_safe_set_attribute_with_complex_types(self):
        """Testa _safe_set_attribute com tipos complexos."""
        mock_span = Mock()

        # Tipos complexos devem ser convertidos para string
        _safe_set_attribute(mock_span, "dict_attr", {"key": "value"})
        _safe_set_attribute(mock_span, "list_attr", [1, 2, 3])
        _safe_set_attribute(mock_span, "tuple_attr", (1, 2))

        # Verificar chamadas com conversão para string
        assert mock_span.set_attribute.call_count == 3
        mock_span.set_attribute.assert_any_call("dict_attr", "{'key': 'value'}")
        mock_span.set_attribute.assert_any_call("list_attr", "[1, 2, 3]")

    @patch("django_coralogix_otel.middleware.trace.get_current_span")
    def test_middleware_with_recording_span(self, mock_get_span):
        """Testa middleware com span ativo."""
        mock_span = Mock()
        mock_span.is_recording.return_value = True
        mock_get_span.return_value = mock_span

        middleware = OpenTelemetryMiddleware(self.get_response)
        request = self.factory.get("/test/")

        # Simular usuário autenticado
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.id = 123
        request.user.get_username.return_value = "testuser"

        # Simular sessão
        request.session = Mock()
        request.session.session_key = "session123"

        middleware(request)

        # Verificar atributos HTTP foram setados
        http_calls = [call for call in mock_span.set_attribute.call_args_list if call[0][0].startswith("http.")]
        assert len(http_calls) >= 6  # method, url, scheme, host, user_agent, target

        # Verificar atributos Django foram setados
        django_calls = [call for call in mock_span.set_attribute.call_args_list if call[0][0].startswith("django.")]
        assert len(django_calls) >= 3  # user.id, username, session.id

    @patch("django_coralogix_otel.middleware.trace.get_current_span")
    def test_middleware_handles_exceptions_gracefully(self, mock_get_span):
        """Testa que middleware trata exceções gracefulmente."""
        mock_span = Mock()
        mock_span.is_recording.return_value = True
        mock_span.set_attribute.side_effect = Exception("Test error")
        mock_get_span.return_value = mock_span

        with patch("django_coralogix_otel.middleware.logger") as mock_logger:
            middleware = OpenTelemetryMiddleware(self.get_response)
            request = self.factory.get("/test/")

            # Não deve levantar exceção
            response = middleware(request)

            # Deve loggar warning (pode ser 1 ou 2 vezes)
            assert mock_logger.warning.call_count >= 1
            warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
            assert any("Failed to set OpenTelemetry attributes" in call for call in warning_calls)

    @patch("django_coralogix_otel.middleware.trace.get_current_span")
    def test_middleware_with_no_span(self, mock_get_span):
        """Testa middleware sem span ativo."""
        mock_get_span.return_value = None

        middleware = OpenTelemetryMiddleware(self.get_response)
        request = self.factory.get("/test/")

        # Não deve levantar exceção
        response = middleware(request)

        # get_response deve ser chamado
        self.get_response.assert_called_once_with(request)

    def test_get_client_ip_with_x_forwarded_for(self):
        """Testa obtenção de IP com X-Forwarded-For."""
        middleware = OpenTelemetryMiddleware(self.get_response)
        request = self.factory.get("/test/")
        request.META = {"HTTP_X_FORWARDED_FOR": "192.168.1.1, 10.0.0.1"}

        ip = middleware.get_client_ip(request)
        assert ip == "192.168.1.1"

    def test_get_client_ip_with_remote_addr(self):
        """Testa obtenção de IP com Remote_Addr."""
        middleware = OpenTelemetryMiddleware(self.get_response)
        request = self.factory.get("/test/")
        request.META = {"REMOTE_ADDR": "192.168.1.2"}

        ip = middleware.get_client_ip(request)
        assert ip == "192.168.1.2"

    def test_get_user_id_authenticated(self):
        """Testa obtenção de user ID para usuário autenticado."""
        middleware = OpenTelemetryMiddleware(self.get_response)
        request = self.factory.get("/test/")
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.id = 123

        user_id = middleware.get_user_id(request)
        assert user_id == "123"

    def test_get_user_id_unauthenticated(self):
        """Testa obtenção de user ID para usuário não autenticado."""
        middleware = OpenTelemetryMiddleware(self.get_response)
        request = self.factory.get("/test/")
        request.user = Mock()
        request.user.is_authenticated = False

        user_id = middleware.get_user_id(request)
        assert user_id == ""

    def test_get_user_id_no_user(self):
        """Testa obtenção de user ID sem objeto user."""
        middleware = OpenTelemetryMiddleware(self.get_response)
        request = self.factory.get("/test/")

        user_id = middleware.get_user_id(request)
        assert user_id == ""

    @patch("django_coralogix_otel.middleware.trace.get_current_span")
    def test_response_status_code_attribute(self, mock_get_span):
        """Testa que status code da response é adicionado como atributo."""
        mock_span = Mock()
        mock_span.is_recording.return_value = True
        mock_get_span.return_value = mock_span

        mock_response = Mock()
        mock_response.status_code = 404

        self.get_response.return_value = mock_response

        middleware = OpenTelemetryMiddleware(self.get_response)
        request = self.factory.get("/test/")

        response = middleware(request)

        # Verificar que status code foi setado
        mock_span.set_attribute.assert_any_call("http.status_code", 404)
