"""
WSGI config for test_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import logging

from django.core.wsgi import get_wsgi_application

logger = logging.getLogger(__name__)

# Inicializar OpenTelemetry antes da aplicação Django
try:
    from django_coralogix_otel import initialize_opentelemetry
    
    # Configurar OpenTelemetry para desenvolvimento (console exporter habilitado)
    if initialize_opentelemetry(enable_console_exporter=True):
        logger.info("✅ OpenTelemetry inicializado com sucesso para Coralogix")
    else:
        logger.warning("⚠️ OpenTelemetry não pôde ser inicializado, continuando sem telemetria")
        
except ImportError as e:
    logger.error(f"❌ Erro ao importar django-coralogix-otel: {e}")
    logger.info("ℹ️ Continuando sem instrumentação OpenTelemetry")
except Exception as e:
    logger.error(f"❌ Erro inesperado ao inicializar OpenTelemetry: {e}")
    logger.info("ℹ️ Continuando sem instrumentação OpenTelemetry")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.settings')

application = get_wsgi_application()