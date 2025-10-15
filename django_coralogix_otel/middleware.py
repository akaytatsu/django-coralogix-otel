"""
Django middleware for OpenTelemetry trace context enhancement.
"""

import logging

from opentelemetry import trace

logger = logging.getLogger(__name__)


def _safe_set_attribute(span, key, value):
    """Define atributo de forma segura, convertendo tipos complexos."""
    if isinstance(value, (str, int, float, bool, type(None))):
        span.set_attribute(key, value)
    elif isinstance(value, (dict, list, tuple)):
        span.set_attribute(key, str(value))
    # Ignorar tipos complexos como ASGIRequest


class OpenTelemetryMiddleware:
    """
    Middleware to enhance trace context with additional information.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get current span
        current_span = trace.get_current_span()

        if current_span and current_span.is_recording():
            try:
                # HTTP Attributes (seguros)
                _safe_set_attribute(current_span, "http.method", request.method)
                _safe_set_attribute(current_span, "http.url", request.build_absolute_uri())
                _safe_set_attribute(current_span, "http.scheme", request.scheme)
                _safe_set_attribute(current_span, "http.host", request.get_host())
                _safe_set_attribute(current_span, "http.user_agent", request.META.get("HTTP_USER_AGENT", ""))
                _safe_set_attribute(current_span, "http.remote_addr", self.get_client_ip(request))
                _safe_set_attribute(current_span, "http.target", request.path)

                # Django Attributes (seguros)
                _safe_set_attribute(current_span, "django.user.id", self.get_user_id(request))
                _safe_set_attribute(current_span, "django.user.username", self.get_username(request))
                _safe_set_attribute(current_span, "django.session.id", self.get_session_id(request))

            except Exception as e:
                logger.warning(f"Failed to set OpenTelemetry attributes: {e}")
                # Continuar sem atributos personalizados

        response = self.get_response(request)

        # Add response attributes
        if current_span and current_span.is_recording():
            try:
                _safe_set_attribute(current_span, "http.status_code", response.status_code)
            except Exception as e:
                logger.warning(f"Failed to set response status code: {e}")

        return response

    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip or ""

    def get_user_id(self, request):
        """Get user ID from request if authenticated."""
        try:
            if hasattr(request, "user") and request.user.is_authenticated:
                return str(request.user.id)
        except Exception:
            pass
        return ""

    def get_username(self, request):
        """Get username from request if authenticated."""
        try:
            if hasattr(request, "user") and request.user.is_authenticated:
                return request.user.get_username()
        except Exception:
            pass
        return ""

    def get_session_id(self, request):
        """Get session ID from request if available."""
        try:
            if hasattr(request, "session") and hasattr(request.session, "session_key"):
                return request.session.session_key or ""
        except Exception:
            pass
        return ""


# Manter o nome antigo para compatibilidade
TraceMiddleware = OpenTelemetryMiddleware
