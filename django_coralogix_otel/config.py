"""
Configuração OpenTelemetry para Django com Coralogix
Implementação completa com suporte a variáveis de ambiente do Kubernetes
"""

import os
import logging
from typing import Dict, Any, Optional
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter
)
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    ConsoleLogExporter
)
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

from .utils import get_coralogix_headers, get_resource_attributes

logger = logging.getLogger(__name__)


def configure_opentelemetry(enable_console_exporter: bool = False) -> bool:
    """
    Configura o OpenTelemetry para tracing, metrics e logging
    com suporte completo às variáveis de ambiente do Kubernetes
    
    Args:
        enable_console_exporter: Se True, habilita exportador console para desenvolvimento
        
    Returns:
        bool: True se a configuração foi bem-sucedida
    """
    try:
        # Verificar se OpenTelemetry deve ser habilitado
        if not _should_enable_opentelemetry():
            logger.info("OpenTelemetry desabilitado por configuração")
            return False

        # Configurar resource com atributos Coralogix e Kubernetes
        resource = Resource.create(get_resource_attributes())
        
        # Configurar tracing
        _configure_tracing(resource, enable_console_exporter)
        
        # Configurar metrics
        _configure_metrics(resource, enable_console_exporter)
        
        # Configurar logging
        _configure_logging(resource, enable_console_exporter)
        
        logger.info("OpenTelemetry configurado com sucesso para Coralogix")
        return True

    except Exception as e:
        logger.error(f"Erro ao configurar OpenTelemetry: {e}")
        # Não levantar exceção para permitir fallback
        return False


def _should_enable_opentelemetry() -> bool:
    """Verifica se OpenTelemetry deve ser habilitado baseado em variáveis de ambiente"""
    # Verificar se variáveis obrigatórias estão presentes
    if not os.getenv("CORALOGIX_PRIVATE_KEY") or not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        logger.warning("Variáveis obrigatórias para OpenTelemetry não encontradas")
        return False
    
    # Verificar se instrumentação está habilitada via variáveis de ambiente
    django_enabled = os.getenv("OTEL_PYTHON_DJANGO_INSTRUMENT", "true").lower() == "true"
    if not django_enabled:
        logger.info("Instrumentação Django desabilitada por configuração")
        return False
        
    return True


def _configure_tracing(resource: Resource, enable_console: bool = False):
    """Configura o tracing OpenTelemetry"""
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    
    # Configurar exportador OTLP para produção
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        otlp_trace_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            headers=get_coralogix_headers()
        )
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))
    
    # Configurar exportador console para desenvolvimento
    if enable_console or os.getenv("OTEL_LOG_LEVEL") == "DEBUG":
        console_exporter = ConsoleSpanExporter()
        tracer_provider.add_span_processor(SimpleSpanProcessor(console_exporter))


def _configure_metrics(resource: Resource, enable_console: bool = False):
    """Configura as métricas OpenTelemetry"""
    exporters = []
    
    # Configurar exportador OTLP para produção
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        otlp_metric_exporter = OTLPMetricExporter(
            endpoint=otlp_endpoint,
            headers=get_coralogix_headers()
        )
        exporters.append(PeriodicExportingMetricReader(otlp_metric_exporter))
    
    # Configurar exportador console para desenvolvimento
    if enable_console or os.getenv("OTEL_LOG_LEVEL") == "DEBUG":
        console_exporter = ConsoleMetricExporter()
        exporters.append(PeriodicExportingMetricReader(console_exporter))
    
    if exporters:
        meter_provider = MeterProvider(resource=resource, metric_readers=exporters)
        metrics.set_meter_provider(meter_provider)


def _configure_logging(resource: Resource, enable_console: bool = False):
    """Configura o logging OpenTelemetry"""
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)
    
    # Configurar exportador OTLP para produção
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        otlp_log_exporter = OTLPLogExporter(
            endpoint=otlp_endpoint,
            headers=get_coralogix_headers()
        )
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))
    
    # Configurar exportador console para desenvolvimento
    if enable_console or os.getenv("OTEL_LOG_LEVEL") == "DEBUG":
        console_exporter = ConsoleLogExporter()
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(console_exporter))
    
    # Configurar handler de logging para Django
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)


def get_tracer(name: Optional[str] = None):
    """Retorna o tracer configurado"""
    return trace.get_tracer(name or __name__)


def get_meter(name: Optional[str] = None):
    """Retorna o meter configurado"""
    return metrics.get_meter(name or __name__)