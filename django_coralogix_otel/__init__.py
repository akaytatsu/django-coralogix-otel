"""
Django Coralogix OpenTelemetry Package
"""

__version__ = "1.0.61"
default_app_config = "django_coralogix_otel.apps.DjangoCoralogixOtelConfig"

import os


def get_gunicorn_config_path():
    """
    Retorna o caminho para o arquivo gunicorn.config.py da biblioteca.
    Esta função é usada pelo entrypoint.sh para encontrar o arquivo de configuração.
    """
    import django_coralogix_otel
    import sys
    import tempfile
    import os

    # Debug: mostrar onde está o pacote
    package_dir = os.path.dirname(django_coralogix_otel.__file__)
    print(f"DEBUG: Package directory: {package_dir}", file=sys.stderr)

    # Tentar encontrar o arquivo no pacote
    config_path = os.path.join(package_dir, "gunicorn_config.py")
    print(f"DEBUG: Looking for config at: {config_path}", file=sys.stderr)
    print(f"DEBUG: Config exists: {os.path.exists(config_path)}", file=sys.stderr)

    if os.path.exists(config_path):
        return config_path

    # Tentar encontrar no local original (desenvolvimento)
    original_path = os.path.normpath(os.path.join(package_dir, "..", "gunicorn.config.py"))
    print(f"DEBUG: Looking for original config at: {original_path}", file=sys.stderr)
    print(f"DEBUG: Original config exists: {os.path.exists(original_path)}", file=sys.stderr)

    if os.path.exists(original_path):
        return original_path

    # Listar arquivos no diretório do pacote para debug
    print(f"DEBUG: Files in package directory:", file=sys.stderr)
    try:
        files = os.listdir(package_dir)
        for f in files:
            if "gunicorn" in f.lower():
                print(f"DEBUG: Found file: {f}", file=sys.stderr)
    except Exception as e:
        print(f"DEBUG: Error listing files: {e}", file=sys.stderr)

    # Se não encontrar em nenhum lugar, criar um arquivo temporário
    try:
        config_content = """
# gunicorn.config.py
# Configuração padrão do Gunicorn para django-coralogix-otel

import multiprocessing
import os

# Configurações básicas
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8080")
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "sync")

# Configurações de performance
timeout = int(os.getenv("GUNICORN_TIMEOUT", 30))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 5))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1000))

# Configurações de logging
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

# Application module - respeitar variável de ambiente
application = os.getenv("GUNICORN_APPLICATION", "conf.asgi:application")

def when_ready(server):
    server.log.info("Gunicorn ready with django-coralogix-otel")
"""

        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
        temp_file.write(config_content)
        temp_file.close()
        print(f"DEBUG: Created temp config at: {temp_file.name}", file=sys.stderr)
        return temp_file.name
    except Exception as e:
        print(f"DEBUG: Error creating temp config: {e}", file=sys.stderr)
        pass

    print("DEBUG: Returning None", file=sys.stderr)
    return None
