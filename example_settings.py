"""
Example Django project configuration using django-coralogix-otel.
"""

# settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Add OpenTelemetry Coralogix integration
    'django_coralogix_otel',
    
    # Your apps
    'myapp',
]

# Middleware - add trace middleware for enhanced context
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # OpenTelemetry trace middleware (optional but recommended)
    'django_coralogix_otel.middleware.TraceMiddleware',
]

# Logging configuration
from django_coralogix_otel.logging_config import LOGGING_CONFIG
LOGGING = LOGGING_CONFIG

# Custom OpenTelemetry configuration (optional)
DJANGO_CORALOGIX_OTEL = {
    'SERVICE_NAME': 'my-awesome-service',
    'SERVICE_VERSION': '2.0.0',
    'ENVIRONMENT': 'production',
    'ENABLE_KAFKA_INSTRUMENTATION': True,
    'CUSTOM_RESOURCE_ATTRIBUTES': {
        'team': 'backend',
        'cost_center': 'engineering',
        'project': 'awesome-project',
    },
    'CUSTOM_LOGGERS': {
        'myapp': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}