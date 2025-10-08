"""
Django Coralogix OpenTelemetry - Auto-instrumentação para Django com Coralogix.

Este pacote fornece integração fácil entre aplicações Django e OpenTelemetry
enviando métricas, traces e logs para o Coralogix.
"""

__version__ = "1.0.0"
__author__ = "Vert Capital"
__email__ = "dev@vert-capital.com"

from .config import configure_opentelemetry
from .entrypoint import main

__all__ = ["configure_opentelemetry", "main"]