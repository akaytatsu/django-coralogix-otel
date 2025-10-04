import os

from django.apps import AppConfig


class DjangoCoralogixOtelConfig(AppConfig):
    """Django AppConfig for OpenTelemetry Coralogix integration."""

    name = "django_coralogix_otel"
    verbose_name = "Django Coralogix OpenTelemetry"

    def ready(self):
        """Initialize OpenTelemetry when Django app is ready."""
        # Only configure if not running with opentelemetry-instrument
        if not os.getenv("OTEL_PYTHON_INSTRUMENTATION_ENABLED"):
            from .otel_config import configure_opentelemetry

            configure_opentelemetry()
