"""
Middleware Django para OpenTelemetry
Implementação completa com atributos Coralogix e tratamento robusto de erros
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    from .config import get_tracer
    from .utils import is_opentelemetry_available
except ImportError:
    # Fallback para quando OpenTelemetry não estiver disponível
    trace = None
    get_tracer = None
    is_opentelemetry_available = lambda: False


class OpenTelemetryMiddleware(MiddlewareMixin):
    """
    Middleware para instrumentação automática de requests Django
    com atributos Coralogix customizados e tratamento robusto de erros
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.tracer = None
        
        # Verificar se OpenTelemetry está disponível e habilitado
        if is_opentelemetry_available():
            try:
                self.tracer = get_tracer("django.middleware")
            except Exception as e:
                logger.warning(f"Erro ao obter tracer OpenTelemetry: {e}")
                self.tracer = None

    def process_request(self, request):
        """Inicia o span para a requisição com atributos Coralogix"""
        if not self.tracer:
            return

        try:
            # Criar span para a requisição
            span_name = self._get_span_name(request)
            self.current_span = self.tracer.start_span(span_name)
            
            # Adicionar atributos HTTP padrão
            self._add_http_attributes(request)
            
            # Adicionar atributos Coralogix customizados
            self._add_coralogix_attributes(request)
            
            # Adicionar atributos específicos do Django
            self._add_django_attributes(request)
            
            request.opentelemetry_span = self.current_span
            request.start_time = time.time()
            
        except Exception as e:
            logger.error(f"Erro ao processar request OpenTelemetry: {e}")
            # Não quebrar a aplicação em caso de erro no middleware

    def process_response(self, request, response):
        """Finaliza o span e adiciona informações da resposta"""
        if not hasattr(request, 'opentelemetry_span') or not self.tracer:
            return response

        try:
            # Calcular tempo de resposta
            duration = time.time() - getattr(request, 'start_time', time.time())
            
            # Adicionar atributos da resposta
            request.opentelemetry_span.set_attribute("http.status_code", response.status_code)
            request.opentelemetry_span.set_attribute("http.response_size", len(response.content))
            request.opentelemetry_span.set_attribute("http.duration", duration)
            
            # Definir status do span baseado no código HTTP
            self._set_span_status(request.opentelemetry_span, response.status_code)
            
            # Finalizar span
            request.opentelemetry_span.end()
            
        except Exception as e:
            logger.error(f"Erro ao processar response OpenTelemetry: {e}")
            # Tentar finalizar o span mesmo em caso de erro
            try:
                if hasattr(request, 'opentelemetry_span'):
                    request.opentelemetry_span.end()
            except Exception:
                pass
        
        return response

    def process_exception(self, request, exception):
        """Registra exceções no span e define status de erro"""
        if hasattr(request, 'opentelemetry_span') and self.tracer:
            try:
                request.opentelemetry_span.record_exception(exception)
                request.opentelemetry_span.set_status(Status(StatusCode.ERROR))
                request.opentelemetry_span.set_attribute("error", True)
                request.opentelemetry_span.set_attribute("error.type", type(exception).__name__)
                request.opentelemetry_span.set_attribute("error.message", str(exception))
            except Exception as e:
                logger.error(f"Erro ao processar exceção OpenTelemetry: {e}")

    def _get_span_name(self, request):
        """Gera o nome do span baseado na requisição"""
        resolver_match = getattr(request, 'resolver_match', None)
        if resolver_match and hasattr(resolver_match, 'view_name'):
            return f"{request.method} {resolver_match.view_name}"
        return f"{request.method} {request.path}"

    def _add_http_attributes(self, request):
        """Adiciona atributos HTTP padrão ao span"""
        self.current_span.set_attribute("http.method", request.method)
        self.current_span.set_attribute("http.url", request.build_absolute_uri())
        self.current_span.set_attribute("http.user_agent", request.META.get('HTTP_USER_AGENT', ''))
        self.current_span.set_attribute("http.client_ip", self._get_client_ip(request))
        self.current_span.set_attribute("http.host", request.get_host())
        self.current_span.set_attribute("http.scheme", request.scheme)

    def _add_coralogix_attributes(self, request):
        """Adiciona atributos Coralogix customizados ao span"""
        import os
        self.current_span.set_attribute("cx.application.name", os.getenv("CORALOGIX_APPLICATION_NAME", "django-app"))
        self.current_span.set_attribute("cx.subsystem.name", os.getenv("CORALOGIX_SUBSYSTEM_NAME", "backend"))
        self.current_span.set_attribute("service.name", os.getenv("OTEL_SERVICE_NAME", "django-application"))
        self.current_span.set_attribute("deployment.environment", os.getenv("OTEL_DEPLOYMENT_ENVIRONMENT", "development"))

    def _add_django_attributes(self, request):
        """Adiciona atributos específicos do Django ao span"""
        resolver_match = getattr(request, 'resolver_match', None)
        if resolver_match:
            if hasattr(resolver_match, 'view_name'):
                self.current_span.set_attribute("django.view_name", resolver_match.view_name)
            if hasattr(resolver_match, 'url_name'):
                self.current_span.set_attribute("django.url_name", resolver_match.url_name)
            if hasattr(resolver_match, 'app_name'):
                self.current_span.set_attribute("django.app_name", resolver_match.app_name)
        
        self.current_span.set_attribute("django.user", str(request.user) if hasattr(request, 'user') else "anonymous")
        self.current_span.set_attribute("django.session", bool(request.session) if hasattr(request, 'session') else False)

    def _set_span_status(self, span, status_code):
        """Define o status do span baseado no código HTTP"""
        if 500 <= status_code <= 599:
            span.set_status(Status(StatusCode.ERROR, f"HTTP {status_code}"))
        elif 400 <= status_code <= 499:
            span.set_status(Status(StatusCode.ERROR, f"HTTP {status_code}"))
        else:
            span.set_status(Status(StatusCode.OK))

    def _get_client_ip(self, request):
        """Extrai o IP real do cliente considerando proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip