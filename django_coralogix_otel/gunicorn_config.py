# gunicorn.config.py
import os

# Configurações do Gunicorn
bind = "0.0.0.0:8080"
workers = 2
threads = 2
worker_class = "uvicorn.workers.UvicornWorker"  # Use UvicornWorker for ASGI
timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 100

# Application
application = "conf.asgi:application"  # Use ASGI application

# Logs
access_logfile = "-"
error_logfile = "-"
loglevel = "info"


def post_fork(server, worker):
    """
    Hook executado após o fork do worker.
    Com auto-instrumentação via opentelemetry-instrument, não precisamos
    configurar o OpenTelemetry manualmente aqui.
    """
    server.log.info("Worker spawned (pid: %s)", worker.pid)

    # Se estiver usando auto-instrumentação, o OpenTelemetry já está configurado
    if os.environ.get("OTEL_PYTHON_INSTRUMENTATION_ENABLED"):
        server.log.info("OpenTelemetry auto-instrumentation detected")
    else:
        server.log.info("OpenTelemetry manual configuration will be handled by Django settings")
