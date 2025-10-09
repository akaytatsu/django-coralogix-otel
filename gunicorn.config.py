# gunicorn.config.py
# Configuração do Gunicorn otimizada para OpenTelemetry e django-coralogix-otel
# Compatível com estratégia híbrida e auto-instrumentação

import multiprocessing
import os

# Configurações básicas do Gunicorn
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8080")
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
threads = int(os.getenv("GUNICORN_THREADS", 2))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "uvicorn.workers.UvicornWorker")

# Configurações de performance
timeout = int(os.getenv("GUNICORN_TIMEOUT", 30))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 5))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1000))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", 100))

# Configurações de logging
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

# Configurações de segurança
limit_request_line = int(os.getenv("GUNICORN_LIMIT_REQUEST_LINE", 4094))
limit_request_fields = int(os.getenv("GUNICORN_LIMIT_REQUEST_FIELDS", 100))
limit_request_field_size = int(os.getenv("GUNICORN_LIMIT_REQUEST_FIELD_SIZE", 8190))

# Configurações específicas para ASGI (se necessário)
if worker_class == "uvicorn.workers.UvicornWorker":
    # Configurações específicas para ASGI
    worker_connections = int(os.getenv("GUNICORN_WORKER_CONNECTIONS", 1000))
    # Para ASGI, ajustar workers baseado na memória disponível
    if os.getenv("GUNICORN_ASGI_OPTIMIZED") == "true":
        workers = min(workers, 4)  # ASGI geralmente usa menos workers

# Configurações de preload para melhor performance
preload_app = os.getenv("GUNICORN_PRELOAD_APP", "false").lower() == "true"

# Configurações de graceful shutdown
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", 30))

# Configurações de proxy
proxy_protocol = os.getenv("GUNICORN_PROXY_PROTOCOL", "false").lower() == "true"
proxy_allow_ips = os.getenv("GUNICORN_PROXY_ALLOW_IPS", "127.0.0.1")

# Configurações de SSL (se necessário)
keyfile = os.getenv("GUNICORN_SSL_KEYFILE")
certfile = os.getenv("GUNICORN_SSL_CERTFILE")
ssl_version = os.getenv("GUNICORN_SSL_VERSION", "TLS")


def when_ready(server):
    """
    Hook executado quando o Gunicorn está pronto para aceitar conexões.
    """
    server.log.info("Gunicorn ready to accept connections")
    server.log.info(f"Bind: {bind}")
    server.log.info(f"Workers: {workers}")
    server.log.info(f"Threads: {threads}")
    server.log.info(f"Worker class: {worker_class}")

    # Log sobre OpenTelemetry
    if os.environ.get("OTEL_PYTHON_INSTRUMENTATION_ENABLED"):
        server.log.info("✅ OpenTelemetry auto-instrumentation enabled")
        server.log.info(f"Service: {os.environ.get('OTEL_SERVICE_NAME', 'unknown')}")
    else:
        server.log.info("ℹ️ OpenTelemetry auto-instrumentation not detected")


def post_fork(server, worker):
    """
    Hook executado após o fork do worker.
    Com auto-instrumentação via opentelemetry-instrument, não precisamos
    configurar o OpenTelemetry manualmente aqui.
    """
    server.log.info(f"Worker spawned (pid: {worker.pid})")

    # Se estiver usando auto-instrumentação, o OpenTelemetry já está configurado
    if os.environ.get("OTEL_PYTHON_INSTRUMENTATION_ENABLED"):
        server.log.info("✅ OpenTelemetry auto-instrumentation active")
        server.log.info(f"📊 Service: {os.environ.get('OTEL_SERVICE_NAME', 'unknown')}")
        server.log.info(f"🌍 Environment: {os.environ.get('OTEL_DEPLOYMENT_ENVIRONMENT', 'unknown')}")
    else:
        server.log.info("ℹ️ OpenTelemetry manual configuration will be handled by Django settings")


def worker_int(worker):
    """
    Hook executado quando um worker recebe um sinal de interrupção.
    """
    worker.log.info("Worker received interrupt signal")


def worker_abort(worker):
    """
    Hook executado quando um worker é abortado.
    """
    worker.log.info("Worker aborted")


def pre_exec(server):
    """
    Hook executado antes do fork do master.
    """
    server.log.info("Master is about to fork workers")


def pre_request(worker, req):
    """
    Hook executado antes de processar cada requisição.
    """
    worker.log.debug(f"Starting request: {req.method} {req.path}")


def post_request(worker, req, environ, resp):
    """
    Hook executado após processar cada requisição.
    """
    worker.log.debug(f"Completed request: {req.method} {req.path} -> {resp.status}")


def worker_exit(server, worker):
    """
    Hook executado quando um worker termina.
    """
    server.log.info(f"Worker exited (pid: {worker.pid})")


# Configurações específicas para django-coralogix-otel
def on_starting(server):
    """
    Hook executado quando o Gunicorn está iniciando.
    """
    server.log.info("=== Gunicorn Starting with django-coralogix-otel ===")
    server.log.info("📦 Package: django-coralogix-otel")
    server.log.info("🎯 Strategy: Hybrid (auto-instrumentation + manual)")
    server.log.info("🔧 OpenTelemetry: Auto-instrumentation enabled")

    # Verificar se as variáveis de ambiente necessárias estão definidas
    if not os.environ.get("CORALOGIX_PRIVATE_KEY"):
        server.log.warning("⚠️ CORALOGIX_PRIVATE_KEY not set")

    if not os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        server.log.warning("⚠️ OTEL_EXPORTER_OTLP_ENDPOINT not set")

    server.log.info("✅ Gunicorn configuration loaded successfully")


# Configurações de worker específicas
worker_tmp_dir = os.getenv("GUNICORN_WORKER_TMP_DIR", "/dev/shm")

# Application ASGI (necessário para workers ASGI)
application = os.getenv("DJANGO_ASGI_APPLICATION", "asgi:application")
