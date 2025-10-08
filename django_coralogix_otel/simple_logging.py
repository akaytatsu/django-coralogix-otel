"""
Simplified logging configuration for Django with OpenTelemetry integration.
This module provides a more robust approach to JSON logging setup.
"""

import logging
import logging.config
import os
from datetime import datetime

from opentelemetry import trace


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

        import json

        return json.dumps(log_entry)


def setup_json_logging():
    """Setup JSON logging with trace context - simplified approach."""
    try:
        # Create formatter and handler directly
        formatter = JSONFormatterWithTrace()
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        # Configure root logger
        root_logger = logging.getLogger()

        # Avoid duplicate handlers
        for existing_handler in root_logger.handlers:
            if isinstance(existing_handler, logging.StreamHandler) and hasattr(existing_handler, "setFormatter"):
                if isinstance(existing_handler.formatter, JSONFormatterWithTrace):
                    # Already configured
                    return

        root_logger.addHandler(handler)
        root_logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

        print("JSON logging with trace context configured successfully")

    except Exception as e:
        print(f"Failed to setup JSON logging: {e}")
        # Fallback to basic logging
        logging.basicConfig(
            level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
