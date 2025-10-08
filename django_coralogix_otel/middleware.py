"""
Middleware Django para integração com OpenTelemetry e Coralogix.

Este middleware adiciona informações customizadas aos spans
do OpenTelemetry para melhor visibilidade no Coralogix.
"""

import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class CoralogixMiddleware(MiddlewareMixin):
    """
    Middleware que adiciona atributos customizados aos spans do OpenTelemetry.
    
    Este middleware deve ser adicionado ao settings.py do Django para
    enriquecer os traces com informações específicas da aplicação.
    """
    
    def process_request(self, request):
        """
        Adiciona atributos ao span atual da requisição HTTP.
        
        Args:
            request: Objeto HttpRequest do Django
        """
        try:
            # Importação tardia para evitar dependências circulares
            from opentelemetry import trace
            
            # Obtém o span atual
            span = trace.get_current_span()
            if span:
                # Adiciona atributos da requisição
                span.set_attribute("http.method", request.method)
                span.set_attribute("http.url", request.build_absolute_uri())
                span.set_attribute("http.user_agent", request.META.get("HTTP_USER_AGENT", ""))
                span.set_attribute("http.remote_addr", self._get_client_ip(request))
                
                # Adiciona atributos específicos do Django
                span.set_attribute("django.user.id", self._get_user_id(request))
                span.set_attribute("django.user.username", self._get_username(request))
                
                # Adiciona atributos da aplicação
                self._add_application_attributes(span)
                
        except ImportError:
            logger.debug("OpenTelemetry não disponível")
        except Exception as e:
            logger.warning(f"Erro ao adicionar atributos ao span: {e}")
    
    def _get_client_ip(self, request):
        """
        Obtém o IP real do cliente.
        
        Args:
            request: Objeto HttpRequest do Django
            
        Returns:
            str: IP do cliente
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def _get_user_id(self, request):
        """
        Obtém o ID do usuário autenticado.
        
        Args:
            request: Objeto HttpRequest do Django
            
        Returns:
            str: ID do usuário ou None
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            return str(request.user.pk)
        return None
    
    def _get_username(self, request):
        """
        Obtém o username do usuário autenticado.
        
        Args:
            request: Objeto HttpRequest do Django
            
        Returns:
            str: Username ou None
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            return getattr(request.user, 'username', None)
        return None
    
    def _add_application_attributes(self, span):
        """
        Adiciona atributos específicos da aplicação.
        
        Args:
            span: Span do OpenTelemetry
        """
        import os
        
        # Atributos da aplicação
        app_name = os.getenv("OTEL_SERVICE_NAME", "django-service")
        span.set_attribute("application.name", app_name)
        
        # Ambiente
        environment = os.getenv("APP_ENVIRONMENT", "production")
        span.set_attribute("application.environment", environment)
        
        # Versão
        version = os.getenv("OTEL_SERVICE_VERSION", "1.0.0")
        span.set_attribute("application.version", version)