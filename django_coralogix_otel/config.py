"""
Configuração OpenTelemetry para Django com Coralogix
"""

import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

logger = logging.getLogger(__name__)


def configure_opentelemetry():
    """
    Configura o OpenTelemetry para tracing, metrics e logging
    """
    try:
        # Configurar resource com atributos Coralogix
        resource = Resource.create({
            "service.name": os.getenv("OTEL_SERVICE_NAME", "django-application"),
            "service.namespace": os.getenv("OTEL_SERVICE_NAMESPACE", "default"),
            "service.version": os.getenv("OTEL_SERVICE_VERSION", "1.0.0"),
            "deployment.environment": os.getenv("OTEL_DEPLOYMENT_ENVIRONMENT", "development"),
            "coralogix.application": os.getenv("CORALOGIX_APPLICATION_NAME", "django-app"),
            "coralogix.subsystem": os.getenv("CORALOGIX_SUBSYSTEM_NAME", "backend"),
        })

        # Configurar tracing
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)

        # Configurar exportador OTLP para tracing
        otlp_trace_exporter = OTLPSpanExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
            headers={
                "Authorization": f"Bearer {os.getenv('CORALOGIX_PRIVATE_KEY')}",
                "CX-Application-Name": os.getenv("CORALOGIX_APPLICATION_NAME", "django-app"),
                "CX-Subsystem-Name": os.getenv("CORALOGIX_SUBSYSTEM_NAME", "backend"),
            }
        )
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))

        # Configurar metrics
        otlp_metric_exporter = OTLPMetricExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
            headers={
                "Authorization": f"Bearer {os.getenv('CORALOGIX_PRIVATE_KEY')}",
                "CX-Application-Name": os.getenv("CORALOGIX_APPLICATION_NAME", "django-app"),
                "CX-Subsystem-Name": os.getenv("CORALOGIX_SUBSYSTEM_NAME", "backend"),
            }
        )
        metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter)
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])

        # Configurar logging
        logger_provider = LoggerProvider(resource=resource)
        set_logger_provider(logger_provider)

        otlp_log_exporter = OTLPLogExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
            headers={
                "Authorization": f"Bearer {os.getenv('CORALOGIX_PRIVATE_KEY')}",
                "CX-Application-Name": os.getenv("CORALOGIX_APPLICATION_NAME", "django-app"),
                "CX-Subsystem-Name": os.getenv("CORALOGIX_SUBSYSTEM_NAME", "backend"),
            }
        )
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))

        # Configurar handler de logging para Django
        handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
        logging.getLogger().addHandler(handler)

        logger.info("OpenTelemetry configurado com sucesso para Coralogix")

    except Exception as e:
        logger.error(f"Erro ao configurar OpenTelemetry: {e}")
        raise


def get_tracer():
    """Retorna o tracer configurado"""
    return trace.get_tracer(__name__)