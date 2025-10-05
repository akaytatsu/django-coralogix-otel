import django
import pytest
from django.conf import settings

# Configura Django para os testes
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-secret-key",
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django_coralogix_otel",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        USE_TZ=True,
        # Configuração de logging simples para testes
        LOGGING_CONFIG="logging.config.dictConfig",
        LOGGING={
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                },
            },
            "root": {
                "handlers": ["console"],
                "level": "INFO",
            },
        },
    )
    django.setup()


@pytest.fixture
def django_setup():
    """Garante que Django está configurado para os testes"""
    pass
