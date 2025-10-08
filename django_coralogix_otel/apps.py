import os

from django.apps import AppConfig


class DjangoCoralogixOtelConfig(AppConfig):
    """Django AppConfig for OpenTelemetry Coralogix integration."""

    name = "django_coralogix_otel"
    verbose_name = "Django Coralogix OpenTelemetry"

    def ready(self):
        """Initialize OpenTelemetry when Django app is ready."""
        # Always configure logging, regardless of instrumentation method
        from .otel_config import setup_logging_format

        setup_logging_format()

        # Only configure tracing/metrics if not running with opentelemetry-instrument
        if not os.getenv("OTEL_PYTHON_INSTRUMENTATION_ENABLED"):
            from .otel_config import configure_opentelemetry

            configure_opentelemetry()
