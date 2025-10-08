"""
Logging configuration for Django with OpenTelemetry integration.
This module provides structured JSON logging with trace context.

Simplified - relies on OpenTelemetry SDK environment variables.
"""

import json
import logging
import os
from datetime import datetime

from opentelemetry import trace


class JSONFormatterWithTrace(logging.Formatter):
    """Custom JSON formatter that includes OpenTelemetry trace context."""

    def format(self, record):
        try:
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
        except Exception as e:
            # Fallback to simple JSON if trace context fails
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "otel_error": str(e),  # Add error info for debugging
            }
            return json.dumps(log_entry)


def get_logging_config():
    """Get logging configuration with OpenTelemetry integration.

    Note: OpenTelemetry SDK automatically handles:
    - OTEL_LOGS_EXPORTER
    - OTEL_EXPORTER_OTLP_ENDPOINT
    - OTEL_EXPORTER_OTLP_HEADERS
    - OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED
    """
    # Default logging configuration with JSON formatter and OpenTelemetry context
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json_with_trace": {
                "()": "django_coralogix_otel.logging_config.JSONFormatterWithTrace",
            },
            "verbose": {
                "format": "{levelname} {asctime} {module} {message}",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json_with_trace",
            },
            "console_verbose": {
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
                "propagate": False,
            },
            "django.request": {
                "handlers": ["console"],
                "level": "ERROR",
                "propagate": False,
            },
            "opentelemetry": {
                "handlers": ["console"],
                "level": "WARNING",  # Reduce noise from OTEL itself
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
        },
    }

    # Use verbose formatter for local development
    environment = os.getenv("APP_ENVIRONMENT", "local")
    if environment == "local":
        logging_config["handlers"]["console"]["formatter"] = "verbose"

    return logging_config


# Export the logging configuration
LOGGING_CONFIG = get_logging_config()
