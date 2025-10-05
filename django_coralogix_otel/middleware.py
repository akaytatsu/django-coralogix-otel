"""
Django middleware for OpenTelemetry trace context enhancement.
"""

import logging

from opentelemetry import trace

logger = logging.getLogger(__name__)


class TraceMiddleware:
    """
    Middleware to enhance trace context with additional information.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get current span
        current_span = trace.get_current_span()

        if current_span and current_span.is_recording():
            # Add request-specific attributes to the span
            current_span.set_attribute("http.method", request.method)
            current_span.set_attribute("http.url", request.build_absolute_uri())
            current_span.set_attribute("http.scheme", request.scheme)
            current_span.set_attribute("http.host", request.get_host())
            current_span.set_attribute("http.user_agent", request.META.get("HTTP_USER_AGENT", ""))
            current_span.set_attribute("http.remote_addr", self.get_client_ip(request))

            # Add Django-specific attributes
            current_span.set_attribute("django.user.id", self.get_user_id(request))
            current_span.set_attribute("django.user.username", self.get_username(request))
            current_span.set_attribute("django.session.id", request.session.session_key or "")

        response = self.get_response(request)

        # Add response attributes
        if current_span and current_span.is_recording():
            current_span.set_attribute("http.status_code", response.status_code)

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
