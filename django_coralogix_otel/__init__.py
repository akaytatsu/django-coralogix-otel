"""
Django Coralogix OpenTelemetry Integration

Um pacote Python para auto-instrumentação OpenTelemetry com Coralogix
para aplicações Django. Implementa estratégia híbrida (auto-instrumentação + manual)
com suporte completo às variáveis de ambiente do Kubernetes.
"""

__version__ = "0.1.0"
__author__ = "Vertc Developers"
__email__ = "dev@vertc.com.br"

from .config import (
    configure_opentelemetry,
    get_tracer,
    get_meter
)
from .middleware import OpenTelemetryMiddleware
from .entrypoint import (
    initialize_opentelemetry,
    auto_initialize,
    get_initialization_status,
    instrument_django,
    hybrid_instrumentation,
    safe_configure_opentelemetry
)
from .utils import (
    validate_environment_variables,
    get_coralogix_headers,
    get_resource_attributes,
    is_opentelemetry_available,
    is_instrumentation_enabled,
    get_enabled_instrumentations,
    configure_django_settings,
    get_otel_config,
    safe_configure_opentelemetry
)

__all__ = [
    # Configuração principal
    "configure_opentelemetry",
    "get_tracer",
    "get_meter",
    
    # Middleware
    "OpenTelemetryMiddleware",
    
    # Entrypoint e inicialização
    "initialize_opentelemetry",
    "auto_initialize",
    "get_initialization_status",
    "instrument_django",
    "hybrid_instrumentation",
    "safe_configure_opentelemetry",
    
    # Utilitários
    "validate_environment_variables",
    "get_coralogix_headers",
    "get_resource_attributes",
    "is_opentelemetry_available",
    "is_instrumentation_enabled",
    "get_enabled_instrumentations",
    "configure_django_settings",
    "get_otel_config",
]