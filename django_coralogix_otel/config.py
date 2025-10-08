"""
Configuração do OpenTelemetry para Django com Coralogix.

Este módulo configura automaticamente tracing, métricas e logging
instrumentation para aplicações Django.
"""

import logging
import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.kafka import KafkaInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

logger = logging.getLogger(__name__)


def get_resource():
    """
    Cria e retorna um Resource OpenTelemetry com informações do serviço.
    
    Returns:
        Resource: Configuração de recursos do OpenTelemetry
    """
    service_name = os.getenv("OTEL_SERVICE_NAME", "django-service")
    
    # Extrai atributos de resource do OTEL_RESOURCE_ATTRIBUTES
    resource_attributes = {}
    if os.getenv("OTEL_RESOURCE_ATTRIBUTES"):
        # Formato: key1=value1,key2=value2
        for pair in os.getenv("OTEL_RESOURCE_ATTRIBUTES").split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                resource_attributes[key.strip()] = value.strip()
    
    # Configurações padrão para Coralogix
    default_attributes = {
        SERVICE_NAME: service_name,
        SERVICE_VERSION: os.getenv("OTEL_SERVICE_VERSION", "1.0.0"),
        "service.namespace": os.getenv("OTEL_SERVICE_NAMESPACE", "default"),
        "deployment.environment": os.getenv("APP_ENVIRONMENT", "production"),
        "cx.application.name": resource_attributes.get("cx.application.name", service_name),
        "cx.subsystem.name": resource_attributes.get("cx.subsystem.name", f"{service_name}-backend"),
    }
    
    # Adiciona atributos customizados do resource
    default_attributes.update(resource_attributes)
    
    return Resource.create(default_attributes)


def setup_tracing():
    """
    Configura tracing do OpenTelemetry.
    """
    resource = get_resource()

    # Verifica se TracerProvider já está configurado
    current_provider = trace.get_tracer_provider()
    if hasattr(current_provider, "resource") and current_provider.resource:
        logger.info("TracerProvider já configurado por auto-instrumentação")
        return

    # Configura TracerProvider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Configura exporters
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    if otlp_endpoint:
        # Produção: OTLP exporter para Coralogix
        try:
            # Adiciona /v1/traces ao endpoint se não tiver
            if not otlp_endpoint.endswith("/v1/traces"):
                if otlp_endpoint.endswith("/"):
                    otlp_endpoint = otlp_endpoint[:-1]
                otlp_endpoint = f"{otlp_endpoint}/v1/traces"
            
            otlp_exporter = OTLPSpanExporter(
                endpoint=otlp_endpoint, 
                insecure=True  # Para comunicação interna do Kubernetes
            )
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)
            logger.info(f"OTLP span exporter configurado com endpoint: {otlp_endpoint}")
        except Exception as e:
            logger.error(f"Falha ao configurar OTLP span exporter: {e}")
            # Fallback para console exporter
            _setup_console_tracing(tracer_provider)
    else:
        # Desenvolvimento: Console exporter
        _setup_console_tracing(tracer_provider)


def _setup_console_tracing(tracer_provider):
    """Configura console exporter como fallback."""
    console_exporter = ConsoleSpanExporter()
    span_processor = BatchSpanProcessor(console_exporter)
    tracer_provider.add_span_processor(span_processor)
    logger.info("Console span exporter configurado")


def setup_metrics():
    """
    Configura métricas do OpenTelemetry.
    """
    resource = get_resource()

    # Verifica se MeterProvider já está configurado
    current_provider = metrics.get_meter_provider()
    if hasattr(current_provider, "resource") and current_provider.resource:
        logger.info("MeterProvider já configurado")
        return

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    if otlp_endpoint:
        # Produção: OTLP exporter para Coralogix
        try:
            # Adiciona /v1/metrics ao endpoint se não tiver
            if not otlp_endpoint.endswith("/v1/metrics"):
                if otlp_endpoint.endswith("/"):
                    otlp_endpoint = otlp_endpoint[:-1]
                otlp_endpoint = f"{otlp_endpoint}/v1/metrics"
            
            metric_reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True),
                export_interval_millis=30000,  # 30 segundos
            )
            meter_provider = MeterProvider(
                resource=resource, metric_readers=[metric_reader]
            )
            metrics.set_meter_provider(meter_provider)
            logger.info(
                f"OTLP metric exporter configurado com endpoint: {otlp_endpoint}"
            )
        except Exception as e:
            logger.error(f"Falha ao configurar OTLP metric exporter: {e}")
            # Fallback para console exporter
            _setup_console_metrics(resource)
    else:
        # Desenvolvimento: Console exporter
        _setup_console_metrics(resource)


def _setup_console_metrics(resource):
    """Configura console metrics exporter como fallback."""
    metric_reader = PeriodicExportingMetricReader(
        ConsoleMetricExporter(),
        export_interval_millis=30000,
    )
    meter_provider = MeterProvider(
        resource=resource, metric_readers=[metric_reader]
    )
    metrics.set_meter_provider(meter_provider)
    logger.info("Console metric exporter configurado")


def setup_instrumentation():
    """
    Configura instrumentação automática para Django e outras bibliotecas.
    """
    try:
        # Django instrumentation
        if not DjangoInstrumentor().is_instrumented_by_opentelemetry:
            DjangoInstrumentor().instrument()
            logger.info("Instrumentação Django habilitada")

        # PostgreSQL instrumentation
        if not Psycopg2Instrumentor().is_instrumented_by_opentelemetry:
            Psycopg2Instrumentor().instrument()
            logger.info("Instrumentação Psycopg2 habilitada")

        # Requests instrumentation
        if not RequestsInstrumentor().is_instrumented_by_opentelemetry:
            RequestsInstrumentor().instrument()
            logger.info("Instrumentação Requests habilitada")

        # Kafka instrumentation (se disponível)
        try:
            if not KafkaInstrumentor().is_instrumented_by_opentelemetry:
                KafkaInstrumentor().instrument()
                logger.info("Instrumentação Kafka habilitada")
        except Exception:
            logger.debug("Instrumentação Kafka não disponível ou já configurada")

        # Logging instrumentation
        LoggingInstrumentor().instrument(set_logging_format=True)
        logger.info("Instrumentação Logging habilitada")

    except Exception as e:
        logger.error(f"Falha ao configurar instrumentação: {e}")


def configure_opentelemetry():
    """
    Função principal para configurar OpenTelemetry.
    
    Esta função verifica se a configuração via variáveis de ambiente
    está ativa e configura manualmente se necessário.
    """
    logger.info("Configurando Django Coralogix OpenTelemetry...")
    
    # Configura apenas se não estiver rodando com opentelemetry-instrument
    if not os.getenv("OTEL_PYTHON_INSTRUMENTATION_ENABLED"):
        logger.info("Configurando OpenTelemetry manualmente...")
        setup_tracing()
        setup_metrics()
        setup_instrumentation()
    else:
        logger.info("OpenTelemetry configurado via auto-instrumentação")
    
    logger.info("Django Coralogix OpenTelemetry configurado com sucesso!")