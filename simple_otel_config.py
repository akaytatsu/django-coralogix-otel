"""
OpenTelemetry configuration for SSO project.
Simplified version that works with opentelemetry-instrument.
"""

import logging
import os

logger = logging.getLogger(__name__)


def configure_opentelemetry():
    """
    Configure OpenTelemetry only if not running with opentelemetry-instrument.
    This prevents conflicts when using auto-instrumentation.
    """
    # Only configure if not running with opentelemetry-instrument
    if not os.getenv("OTEL_PYTHON_INSTRUMENTATION_ENABLED"):
        try:
            # Import OpenTelemetry modules only when needed
            from opentelemetry import metrics, trace
            from opentelemetry.sdk.resources import Resource

            # Basic resource configuration
            resource = Resource.create(
                {
                    "service.name": os.getenv("OTEL_SERVICE_NAME", "sso-server"),
                    "deployment.environment": os.getenv("APP_ENVIRONMENT", "production"),
                }
            )

            logger.info("OpenTelemetry configured manually")

        except ImportError:
            logger.warning("OpenTelemetry not available, skipping configuration")
        except Exception as e:
            logger.error(f"Failed to configure OpenTelemetry: {e}")
    else:
        logger.info("OpenTelemetry configured via auto-instrumentation")


# Configure only when imported manually
if not os.getenv("OTEL_PYTHON_INSTRUMENTATION_ENABLED"):
    configure_opentelemetry()
