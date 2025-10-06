#!/usr/bin/env python
"""Test script to verify logging configuration works in Django 3.2 and 5.2"""

import os
import sys
import django
from django.conf import settings

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'django_coralogix_otel',
        ],
        LOGGING={},  # Empty to test automatic configuration
    )

django.setup()

def test_logging():
    """Test if JSON logging with trace context works."""
    print("Testing Django Coralogix OpenTelemetry logging...")
    
    # Import and setup logging
    from django_coralogix_otel.simple_logging import setup_json_logging
    setup_json_logging()
    
    # Test logging
    logger = logging.getLogger('test')
    logger.info("Test message with trace context")
    logger.warning("Warning message")
    logger.error("Error message")
    
    print("✅ Logging test completed successfully!")
    print("Check the output above to see if JSON formatting is working.")

if __name__ == '__main__':
    test_logging()