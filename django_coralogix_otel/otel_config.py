"""
OpenTelemetry configuration for Django with Coralogix integration.
This module sets up tracing, metrics, and logging instrumentation.
"""

import json
import logging
import os
import threading
from datetime import datetime

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

logger = logging.getLogger(__name__)


class JSONFormatterWithTrace(logging.Formatter):
    """Custom JSON formatter that includes OpenTelemetry trace context."""

    def format(self, record):
        # Get current span from OpenTelemetry context
        span = trace.get_current_span()
        trace_id = None
        span_id = None

        if span and span.get_span_context():
            span_context = span.get_span_context()
            if span_context.is_valid:
                trace_id = format(span_context.trace_id, "032x")
                span_id = format(span_context.span_id, "016x")

        # Create log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": threading.current_thread().name,
            "process": os.getpid(),
        }

        # Add OpenTelemetry trace context if available
        if trace_id:
            log_entry["trace_id"] = trace_id
        if span_id:
            log_entry["span_id"] = span_id

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
            }:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


def get_resource():
    """Create and return OpenTelemetry Resource with service information."""
    # Get Django settings if available
    try:
        from django.conf import settings
        custom_config = getattr(settings, 'DJANGO_CORALOGIX_OTEL', {})
    except ImportError:
        custom_config = {}

    resource_attrs = {
        SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", custom_config.get('SERVICE_NAME', 'django-service')),
        SERVICE_VERSION: os.getenv("OTEL_SERVICE_VERSION", custom_config.get('SERVICE_VERSION', '1.0.0')),
        "service.namespace": os.getenv("OTEL_SERVICE_NAMESPACE", "default"),
        "deployment.environment": os.getenv("APP_ENVIRONMENT", custom_config.get('ENVIRONMENT', 'local')),
        "cx.application.name": os.getenv("OTEL_SERVICE_NAME", custom_config.get('SERVICE_NAME', 'django-service')),
        "cx.subsystem.name": os.getenv("OTEL_SERVICE_NAME", custom_config.get('SERVICE_NAME', 'django-service')) + "-backend",
    }

    # Add custom resource attributes
    custom_attrs = custom_config.get('CUSTOM_RESOURCE_ATTRIBUTES', {})
    resource_attrs.update(custom_attrs)

    return Resource.create(resource_attrs)


def setup_tracing():
    """Setup OpenTelemetry tracing."""
    resource = get_resource()

    # Check if TracerProvider is already configured (by auto-instrumentation)
    current_provider = trace.get_tracer_provider()
    if hasattr(current_provider, "resource") and current_provider.resource:
        logger.info("TracerProvider already configured by auto-instrumentation")
        return

    # Configure TracerProvider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Setup exporters
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    otlp_headers = os.getenv("OTEL_EXPORTER_OTLP_HEADERS")

    if otlp_endpoint:
        # Production: OTLP exporter
        try:
            exporter_kwargs = {"endpoint": otlp_endpoint}
            
            # Add headers for authentication if provided
            if otlp_headers:
                headers = {}
                for header in otlp_headers.split(','):
                    key, value = header.split('=', 1)
                    headers[key.strip()] = value.strip()
                exporter_kwargs["headers"] = headers
            
            otlp_exporter = OTLPSpanExporter(**exporter_kwargs)
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)
            logger.info(f"OTLP span exporter configured with endpoint: {otlp_endpoint}")
        except Exception as e:
            logger.error(f"Failed to configure OTLP span exporter: {e}")
            # Fallback to console exporter
            console_exporter = ConsoleSpanExporter()
            span_processor = BatchSpanProcessor(console_exporter)
            tracer_provider.add_span_processor(span_processor)
    else:
        # Development: Console exporter
        console_exporter = ConsoleSpanExporter()
        span_processor = BatchSpanProcessor(console_exporter)
        tracer_provider.add_span_processor(span_processor)
        logger.info("Console span exporter configured")


def setup_metrics():
    """Setup OpenTelemetry metrics."""
    resource = get_resource()

    # Check if MeterProvider is already configured
    current_provider = metrics.get_meter_provider()
    if hasattr(current_provider, "resource") and current_provider.resource:
        logger.info("MeterProvider already configured")
        return

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    otlp_headers = os.getenv("OTEL_EXPORTER_OTLP_HEADERS")

    if otlp_endpoint:
        # Production: OTLP exporter
        try:
            exporter_kwargs = {"endpoint": otlp_endpoint}
            
            # Add headers for authentication if provided
            if otlp_headers:
                headers = {}
                for header in otlp_headers.split(','):
                    key, value = header.split('=', 1)
                    headers[key.strip()] = value.strip()
                exporter_kwargs["headers"] = headers
            
            metric_reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(**exporter_kwargs),
                export_interval_millis=30000,  # 30 seconds
            )
            meter_provider = MeterProvider(
                resource=resource, metric_readers=[metric_reader]
            )
            metrics.set_meter_provider(meter_provider)
            logger.info(
                f"OTLP metric exporter configured with endpoint: {otlp_endpoint}"
            )
        except Exception as e:
            logger.error(f"Failed to configure OTLP metric exporter: {e}")
            # Fallback to console exporter
            metric_reader = PeriodicExportingMetricReader(
                ConsoleMetricExporter(),
                export_interval_millis=30000,
            )
            meter_provider = MeterProvider(
                resource=resource, metric_readers=[metric_reader]
            )
            metrics.set_meter_provider(meter_provider)
    else:
        # Development: Console exporter
        metric_reader = PeriodicExportingMetricReader(
            ConsoleMetricExporter(),
            export_interval_millis=30000,
        )
        meter_provider = MeterProvider(
            resource=resource, metric_readers=[metric_reader]
        )
        metrics.set_meter_provider(meter_provider)
        logger.info("Console metric exporter configured")


def setup_instrumentation():
    """Setup automatic instrumentation for Django and other libraries."""
    try:
        # Get Django settings if available
        try:
            from django.conf import settings
            custom_config = getattr(settings, 'DJANGO_CORALOGIX_OTEL', {})
        except ImportError:
            custom_config = {}

        # Django instrumentation
        if not DjangoInstrumentor().is_instrumented_by_opentelemetry:
            DjangoInstrumentor().instrument()
            logger.info("Django instrumentation enabled")

        # PostgreSQL instrumentation
        if not Psycopg2Instrumentor().is_instrumented_by_opentelemetry:
            Psycopg2Instrumentor().instrument()
            logger.info("Psycopg2 instrumentation enabled")

        # Requests instrumentation
        if not RequestsInstrumentor().is_instrumented_by_opentelemetry:
            RequestsInstrumentor().instrument()
            logger.info("Requests instrumentation enabled")

        # Kafka instrumentation (if enabled)
        if custom_config.get('ENABLE_KAFKA_INSTRUMENTATION', True):
            try:
                from opentelemetry.instrumentation.kafka_python import KafkaPythonInstrumentor
                if not KafkaPythonInstrumentor().is_instrumented_by_opentelemetry:
                    KafkaPythonInstrumentor().instrument()
                    logger.info("Kafka Python instrumentation enabled")
            except ImportError:
                logger.debug("Kafka Python instrumentation not available")

        # Logging instrumentation with JSON formatting and trace context
        from opentelemetry._logs import set_logger_provider
        from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
        from opentelemetry.sdk._logs import LoggerProvider
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

        # Check if LoggerProvider is already configured
        if not hasattr(logging.getLogger(), "_otel_instrumented"):
            # Setup OTLP log exporter for structured logging
            otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
            otlp_headers = os.getenv("OTEL_EXPORTER_OTLP_HEADERS")
            
            if otlp_endpoint:
                try:
                    exporter_kwargs = {"endpoint": otlp_endpoint}
                    
                    # Add headers for authentication if provided
                    if otlp_headers:
                        headers = {}
                        for header in otlp_headers.split(','):
                            key, value = header.split('=', 1)
                            headers[key.strip()] = value.strip()
                        exporter_kwargs["headers"] = headers
                    
                    logger_provider = LoggerProvider(resource=get_resource())
                    log_exporter = OTLPLogExporter(**exporter_kwargs)
                    logger_provider.add_log_record_processor(
                        BatchLogRecordProcessor(log_exporter)
                    )
                    set_logger_provider(logger_provider)
                    logger.info("OTLP log exporter configured")
                except Exception as e:
                    logger.error(f"Failed to configure OTLP log exporter: {e}")

            # Configure logging instrumentation with custom formatter
            LoggingInstrumentor().instrument(
                set_logging_format=False,  # Don't auto-set format, we'll handle it
                log_level=logging.INFO,
                logger_provider=(
                    logger_provider if "logger_provider" in locals() else None
                ),
            )

            # Mark as instrumented to avoid duplicate setup
            logging.getLogger()._otel_instrumented = True

            logger.info("Logging instrumentation enabled with structured format")

    except Exception as e:
        logger.error(f"Failed to setup instrumentation: {e}")


def setup_logging_format():
    """Configure logging with JSON formatter and OpenTelemetry context."""
    # Apply JSON formatter to all handlers
    root_logger = logging.getLogger()

    for handler in root_logger.handlers:
        if not isinstance(handler.formatter, JSONFormatterWithTrace):
            handler.setFormatter(JSONFormatterWithTrace())

    # Configure Django loggers if settings are available
    try:
        from django.conf import settings

        if hasattr(settings, "LOGGING"):
            loggers = settings.LOGGING.get("loggers", {})
            for logger_name, logger_config in loggers.items():
                logger_obj = logging.getLogger(logger_name)
                for handler in logger_obj.handlers:
                    if not isinstance(handler.formatter, JSONFormatterWithTrace):
                        handler.setFormatter(JSONFormatterWithTrace())
    except ImportError:
        pass  # Django not available yet


def configure_opentelemetry():
    """Main function to configure OpenTelemetry."""
    # Only configure if not running with opentelemetry-instrument
    if not os.getenv("OTEL_PYTHON_INSTRUMENTATION_ENABLED"):
        logger.info("Configuring OpenTelemetry manually...")
        setup_tracing()
        setup_metrics()
        setup_instrumentation()
        setup_logging_format()
    else:
        logger.info("OpenTelemetry configured via auto-instrumentation")
        # Still setup logging format even with auto-instrumentation
        setup_logging_format()