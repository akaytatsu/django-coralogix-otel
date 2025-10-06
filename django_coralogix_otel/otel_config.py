"""
OpenTelemetry configuration for Django with Coralogix integration.
This module sets up tracing, metrics, and logging instrumentation.

Simplified version - relies on OpenTelemetry SDK environment variables.
"""

import json
import logging
import logging.config
import os
from datetime import datetime

from opentelemetry import trace, metrics
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


def setup_logging_format():
    """Setup JSON logging format with trace context."""
    # Configure Django logging with JSON formatter
    try:
        from django.conf import settings

        # Get existing logging config or create default
        logging_config = getattr(settings, "LOGGING", {})

        # Ensure version is specified
        if "version" not in logging_config:
            logging_config["version"] = 1

        # Update formatters - check if already exists
        if "formatters" not in logging_config:
            logging_config["formatters"] = {}

        if "json_with_trace" not in logging_config["formatters"]:
            # Try multiple import paths for compatibility
            formatter_paths = [
                "django_coralogix_otel.logging_config.JSONFormatterWithTrace",
                "django_coralogix_otel.otel_config.JSONFormatterWithTrace",
            ]

            # Use the first available path
            formatter_path = formatter_paths[0]  # Default to logging_config
            logging_config["formatters"]["json_with_trace"] = {
                "()": formatter_path,
            }

        # Update handlers to use JSON formatter
        if "handlers" not in logging_config:
            logging_config["handlers"] = {}

        # Create console handler if it doesn't exist
        if "console" not in logging_config["handlers"]:
            logging_config["handlers"]["console"] = {
                "class": "logging.StreamHandler",
                "formatter": "json_with_trace",
            }
        else:
            # Update existing console handler only if it doesn't have json_with_trace
            if "formatter" not in logging_config["handlers"]["console"]:
                logging_config["handlers"]["console"]["formatter"] = "json_with_trace"

        # Update root logger
        if "root" not in logging_config:
            logging_config["root"] = {}

        if "handlers" not in logging_config["root"]:
            logging_config["root"]["handlers"] = []

        if "console" not in logging_config["root"]["handlers"]:
            logging_config["root"]["handlers"].append("console")

        # Apply configuration
        logging.config.dictConfig(logging_config)
        logger.info("JSON logging with trace context configured")

    except ImportError as e:
        logger.error(f"Failed to import logging configuration: {e}")
        # Fallback to basic logging configuration
        try:
            fallback_config = {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "json_with_trace": {
                        "()": "django_coralogix_otel.otel_config.JSONFormatterWithTrace",
                    },
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "json_with_trace",
                    },
                },
                "root": {
                    "handlers": ["console"],
                    "level": os.getenv("LOG_LEVEL", "INFO"),
                },
            }
            logging.config.dictConfig(fallback_config)
            logger.info("Fallback JSON logging configured")
        except Exception as fallback_error:
            logger.error(f"Failed to configure fallback logging: {fallback_error}")
    except Exception as e:
        logger.error(f"Failed to setup logging format: {e}")


def configure_opentelemetry():
    """Main function to configure OpenTelemetry.

    This function should be called from Django settings.py.
    It detects if auto-instrumentation is enabled and configures accordingly.
    """
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


# Configure OpenTelemetry when module is imported (only for manual setup)
# This allows the module to work both with auto-instrumentation and manual setup
if not os.getenv("OTEL_PYTHON_INSTRUMENTATION_ENABLED"):
    configure_opentelemetry()
