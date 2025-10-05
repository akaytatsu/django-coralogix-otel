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
    )
    django.setup()


@pytest.fixture
def django_setup():
    """Garante que Django está configurado para os testes"""
    pass
