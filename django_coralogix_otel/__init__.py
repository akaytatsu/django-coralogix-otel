"""
Django Coralogix OpenTelemetry Integration

Um pacote Python para auto-instrumentação OpenTelemetry com Coralogix
para aplicações Django. Implementa estratégia híbrida (auto-instrumentação + manual)
com suporte completo às variáveis de ambiente do Kubernetes.
"""

__version__ = "1.0.34"
__author__ = "Thiago Freitas"
__email__ = "thiagosistemas3@gmail.com"

from .config import configure_opentelemetry, get_meter, get_tracer
from .entrypoint import (
    auto_initialize,
    get_initialization_status,
    hybrid_instrumentation,
    initialize_opentelemetry,
    instrument_django,
    safe_configure_opentelemetry,
)
from .middleware import OpenTelemetryMiddleware
from .utils import (
    configure_django_settings,
    get_coralogix_headers,
    get_enabled_instrumentations,
    get_otel_config,
    get_resource_attributes,
    is_instrumentation_enabled,
    is_opentelemetry_available,
    safe_configure_opentelemetry,
    validate_environment_variables,
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
