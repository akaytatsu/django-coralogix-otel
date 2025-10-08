"""
Django Coralogix OpenTelemetry Package
"""

__version__ = "1.0.37"
default_app_config = "django_coralogix_otel.apps.DjangoCoralogixOtelConfig"

import os


def get_gunicorn_config_path():
    """
    Retorna o caminho para o arquivo gunicorn.config.py da biblioteca.
    Esta função é usada pelo entrypoint.sh para encontrar o arquivo de configuração.
    """
    import django_coralogix_otel
    package_dir = os.path.dirname(django_coralogix_otel.__file__)
    config_path = os.path.join(package_dir, '..', 'gunicorn.config.py')

    # Normaliza o caminho para remover referências relativas
    config_path = os.path.normpath(config_path)

    if os.path.exists(config_path):
        return config_path
    return None
