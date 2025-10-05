"""
Logging configuration for Django with OpenTelemetry integration.
This module provides structured JSON logging with trace context.

Simplified - relies on OpenTelemetry SDK environment variables.
"""

import os


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
                "()": "django_coralogix_otel.otel_config.JSONFormatterWithTrace",
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
