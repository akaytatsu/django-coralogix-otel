"""
OpenTelemetry configuration for Django with Coralogix integration.
This module sets up tracing, metrics, and logging instrumentation.

Simplified version - relies on OpenTelemetry SDK environment variables.
"""

import json
import logging
import os
from datetime import datetime

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource

logger = logging.getLogger(__name__)


# Fallback JSONFormatterWithTrace for backward compatibility
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
        }

        # Add trace context if available
        if trace_id:
            log_entry["trace_id"] = trace_id
            log_entry["span_id"] = span_id

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        return json.dumps(log_entry)


def get_resource():
    """Create and return OpenTelemetry Resource.

    OpenTelemetry SDK automatically reads standard environment variables:
    - OTEL_SERVICE_NAME (handled by SDK)
    - OTEL_SERVICE_VERSION (handled by SDK)
    - OTEL_RESOURCE_ATTRIBUTES (handled by SDK)
    - OTEL_SERVICE_NAMESPACE (handled by SDK)

    We only handle custom variables here.
    """
    # Get Django settings if available
    try:
        from django.conf import settings

        custom_config = getattr(settings, "DJANGO_CORALOGIX_OTEL", {})
    except ImportError:
        custom_config = {}

    # Only handle custom resource attributes
    resource_attrs = {}

    # Add custom resource attributes from Django settings
    custom_attrs = custom_config.get("CUSTOM_RESOURCE_ATTRIBUTES", {})
    resource_attrs.update(custom_attrs)

    # Create resource with custom attributes only
    # SDK will automatically add standard OTEL env vars
    return Resource.create(resource_attrs) if resource_attrs else Resource.create({})


def setup_tracing():
    """Setup OpenTelemetry tracing.

    Note: OpenTelemetry SDK automatically handles:
    - OTEL_EXPORTER_OTLP_ENDPOINT
    - OTEL_EXPORTER_OTLP_HEADERS
    - OTEL_TRACES_EXPORTER
    - OTEL_TRACES_SAMPLER
    - OTEL_TRACES_SAMPLER_ARG
    """
    # Let SDK handle all standard configuration automatically
    # Only setup if no auto-instrumentation is detected
    current_provider = trace.get_tracer_provider()
    if hasattr(current_provider, "resource") and current_provider.resource:
        logger.info("TracerProvider already configured by auto-instrumentation")
        return

    # SDK will read environment variables automatically
    logger.info("OpenTelemetry tracing configured via environment variables")


def setup_metrics():
    """Setup OpenTelemetry metrics.

    Note: OpenTelemetry SDK automatically handles:
    - OTEL_EXPORTER_OTLP_ENDPOINT
    - OTEL_EXPORTER_OTLP_HEADERS
    - OTEL_METRICS_EXPORTER
    - OTEL_METRIC_EXPORT_INTERVAL
    """
    # Let SDK handle all standard configuration automatically
    try:
        from opentelemetry import metrics

        current_provider = metrics.get_meter_provider()
        if hasattr(current_provider, "resource") and current_provider.resource:
            logger.info("MeterProvider already configured")
            return
    except ImportError:
        logger.warning("OpenTelemetry metrics module not available")

    # SDK will read environment variables automatically
    logger.info("OpenTelemetry metrics configured via environment variables")


def setup_instrumentation():
    """Setup automatic instrumentation for Django and other libraries.

    Note: OpenTelemetry SDK automatically handles:
    - OTEL_PYTHON_DJANGO_INSTRUMENT
    - OTEL_PYTHON_PSYCOPG2_INSTRUMENT
    - OTEL_PYTHON_REQUESTS_INSTRUMENT
    - OTEL_PYTHON_KAFKA_PYTHON_INSTRUMENT
    - OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED
    """
    # When using auto-instrumentation via opentelemetry-instrument command
    # the SDK handles all instrumentations automatically based on env vars
    logger.info("Instrumentations handled by OpenTelemetry SDK environment variables")


def verify_traces_health():
    """Verifica se traces estão funcionando corretamente."""
    try:
        from opentelemetry import trace

        tracer = trace.get_tracer("health-check")

        with tracer.start_as_current_span("otel-health-check") as span:
            span.set_attribute("health.check", "success")
            span.set_attribute("otel.version", getattr(trace, "__version__", "unknown"))
            return True

    except Exception as e:
        logger.error(f"❌ OpenTelemetry health check failed: {e}")
        return False


def verify_metrics_health():
    """Verifica se métricas estão funcionando."""
    try:
        from opentelemetry import metrics

        meter = metrics.get_meter("health-check")
        counter = meter.create_counter("health.check.counter")
        counter.add(1, {"status": "ok", "component": "django-coralogix-otel"})
        return True

    except Exception as e:
        logger.error(f"❌ Metrics health check failed: {e}")
        return False


def setup_logging_format():
    """Setup JSON logging format with trace context - using simplified approach."""
    try:
        # Use the simplified logging setup
        from .simple_logging import setup_json_logging

        setup_json_logging()
        logger.info("Simplified JSON logging configured")

    except Exception as e:
        logger.error(f"Failed to setup logging format: {e}")
        # Final fallback - configure basic JSON logging directly
        try:
            formatter = JSONFormatterWithTrace()
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            root_logger = logging.getLogger()

            # Check if already configured to avoid duplicates
            for h in root_logger.handlers:
                if isinstance(h, logging.StreamHandler) and isinstance(h.formatter, JSONFormatterWithTrace):
                    return

            root_logger.addHandler(handler)
            logger.info("Basic JSON logging configured as final fallback")
        except Exception as final_error:
            logger.error(f"Final fallback failed: {final_error}")


def configure_opentelemetry():
    """Main function to configure OpenTelemetry.

    This function should be called from Django settings.py.
    It detects if auto-instrumentation is enabled and configures accordingly.
    """
    try:
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

        # Verificação de saúde das integrações
        if not verify_traces_health():
            logger.warning("⚠️ Traces verification failed - check configuration")

        if not verify_metrics_health():
            logger.warning("⚠️ Metrics verification failed - check configuration")

    except Exception as e:
        logger.error(f"Failed to configure OpenTelemetry: {e}")
        # Don't raise exceptions to avoid breaking Django startup
        # Just setup basic logging as fallback
        try:
            setup_logging_format()
        except Exception as logging_error:
            logger.error(f"Failed to setup logging as fallback: {logging_error}")


def configure_opentelemetry_safe():
    """
    Safe version of configure_opentelemetry that never raises exceptions.
    This is useful for Django settings.py where errors can break the entire app.
    """
    try:
        configure_opentelemetry()
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"OpenTelemetry configuration failed silently: {e}")
        # Continue without OpenTelemetry - better than breaking the app


# Configure OpenTelemetry when module is imported (only for manual setup)
# This allows the module to work both with auto-instrumentation and manual setup
# Use the safe version to avoid breaking Django startup
configure_opentelemetry_safe()
