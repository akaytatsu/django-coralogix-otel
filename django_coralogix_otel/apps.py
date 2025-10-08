import os

from django.apps import AppConfig


class DjangoCoralogixOtelConfig(AppConfig):
    """Django AppConfig for OpenTelemetry Coralogix integration."""

    name = "django_coralogix_otel"
    verbose_name = "Django Coralogix OpenTelemetry"

    def ready(self):
        """Initialize OpenTelemetry when Django app is ready."""
        # Skip configuration during Django management commands that might fail
        # with database errors when OpenTelemetry is involved
        import sys

        # Check if we're running a management command that might be affected
        if "manage.py" in sys.argv and any(
            cmd in sys.argv
            for cmd in [
                "showmigrations",
                "migrate",
                "sqlmigrate",
                "sqlflush",
                "dbshell",
                "inspectdb",
                "loaddata",
                "dumpdata",
            ]
        ):
            # For these commands, only setup minimal logging to avoid interference
            try:
                from .otel_config import setup_logging_format

                setup_logging_format()
            except Exception:
                pass  # Silently ignore errors during sensitive commands
            return

        # For all other cases, proceed with full setup
        try:
            # Always configure logging, regardless of instrumentation method
            from .otel_config import setup_logging_format

            setup_logging_format()

            # Only configure tracing/metrics if not running with opentelemetry-instrument
            if not os.getenv("OTEL_PYTHON_INSTRUMENTATION_ENABLED"):
                from .otel_config import configure_opentelemetry

                configure_opentelemetry()
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error in DjangoCoralogixOtelConfig.ready(): {e}")
            # Don't raise exceptions to avoid breaking Django startup
