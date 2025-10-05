"""
Logging configuration for Django with OpenTelemetry integration.
This module provides structured JSON logging with trace context.
"""

import os


def get_logging_config():
    """Get logging configuration with OpenTelemetry integration."""

    # Get Django settings if available
    try:
        from django.conf import settings

        custom_config = getattr(settings, "DJANGO_CORALOGIX_OTEL", {})
    except ImportError:
        custom_config = {}

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

    # Add custom loggers from configuration
    custom_loggers = custom_config.get("CUSTOM_LOGGERS", {})
    if custom_loggers:
        logging_config["loggers"].update(custom_loggers)

    # Use verbose formatter for local development
    environment = os.getenv("APP_ENVIRONMENT", custom_config.get("ENVIRONMENT", "local"))
    if environment == "local":
        logging_config["handlers"]["console"]["formatter"] = "verbose"

    return logging_config


# Export the logging configuration
LOGGING_CONFIG = get_logging_config()
