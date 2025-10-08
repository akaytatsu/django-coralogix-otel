"""
Django Coralogix OpenTelemetry Integration

Um pacote Python para auto-instrumentação OpenTelemetry com Coralogix
para aplicações Django.
"""

__version__ = "0.1.0"
__author__ = "Vertc Developers"
__email__ = "dev@vertc.com.br"

from .config import configure_opentelemetry
from .middleware import OpenTelemetryMiddleware
from .entrypoint import initialize_opentelemetry

__all__ = [
    "configure_opentelemetry",
    "OpenTelemetryMiddleware", 
    "initialize_opentelemetry",
]