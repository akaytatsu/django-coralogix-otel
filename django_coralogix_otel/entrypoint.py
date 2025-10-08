"""
Módulo de entrypoint para Django Coralogix OpenTelemetry.

Este módulo fornece um script de entrypoint que pode ser usado
em containers Docker para inicializar aplicações Django com
instrumentação OpenTelemetry.
"""

import os
import sys
import subprocess
import logging

logger = logging.getLogger(__name__)


def setup_opentelemetry_env():
    """
    Configura variáveis de ambiente do OpenTelemetry.
    """
    # Nome do serviço (obrigatório)
    if not os.getenv("OTEL_SERVICE_NAME"):
        service_name = os.getenv("OTEL_SERVICE_NAME", "django-service")
        os.environ["OTEL_SERVICE_NAME"] = service_name
        logger.warning(f"OTEL_SERVICE_NAME não definido, usando padrão: {service_name}")

    # Endpoint do OTLP
    otlp_ip = os.getenv("OTEL_IP")
    if otlp_ip and not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        endpoint = f"http://{otlp_ip}:4317"
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = endpoint
        logger.info(f"OTEL_EXPORTER_OTLP_ENDPOINT configurado: {endpoint}")

    # Configurações de instrumentação
    env_vars = {
        "OTEL_PYTHON_INSTRUMENTATION_ENABLED": "true",
        "OTEL_PYTHON_DJANGO_INSTRUMENT": "true",
        "OTEL_PYTHON_REQUESTS_INSTRUMENT": "true",
        "OTEL_PYTHON_PSYCOPG2_INSTRUMENT": "true",
        "OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED": "true",
        "OTEL_TRACES_EXPORTER": "otlp",
        "OTEL_METRICS_EXPORTER": "otlp",
        "OTEL_LOGS_EXPORTER": "otlp",
        "OTEL_PROPAGATORS": "tracecontext,baggage",
        "OTEL_TRACES_SAMPLER": "always_on",
        "OTEL_BSP_SCHEDULE_DELAY": "5000",
        "OTEL_BSP_MAX_QUEUE_SIZE": "2048",
        "OTEL_BSP_MAX_EXPORT_BATCH_SIZE": "512",
        "OTEL_BSP_EXPORT_TIMEOUT": "30000",
        "OTEL_METRIC_EXPORT_INTERVAL": "30000",
    }

    # Aplica variáveis de ambiente se não estiverem definidas
    for key, value in env_vars.items():
        if not os.getenv(key):
            os.environ[key] = value
            logger.debug(f"Variável de ambiente configurada: {key}={value}")

    # Configuração para desenvolvimento local
    if os.getenv("APP_ENVIRONMENT") == "local" and not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        logger.info("Ambiente de desenvolvimento detectado, usando console exporters")
        os.environ["OTEL_TRACES_EXPORTER"] = "console"
        os.environ["OTEL_METRICS_EXPORTER"] = "console"
        os.environ["OTEL_LOGS_EXPORTER"] = "console"


def run_django_command(cmd_args):
    """
    Executa comandos Django com instrumentação OpenTelemetry.
    
    Args:
        cmd_args (list): Lista de argumentos do comando
    """
    # Constrói o comando com opentelemetry-instrument
    full_cmd = ["opentelemetry-instrument"] + cmd_args
    
    logger.info(f"Executando: {' '.join(full_cmd)}")
    
    try:
        # Executa o comando
        result = subprocess.run(full_cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        logger.error(f"Falha ao executar comando: {e}")
        return e.returncode
    except FileNotFoundError:
        logger.error("opentelemetry-instrument não encontrado. Verifique a instalação.")
        sys.exit(1)


def setup_django():
    """
    Executa setup inicial do Django.
    """
    if os.getenv("SKIP_DJANGO_SETUP") == "true":
        logger.info("Setup do Django pulado (SKIP_DJANGO_SETUP=true)")
        return 0

    logger.info("=== Django Setup ===")

    commands = [
        ["python", "manage.py", "migrate", "--no-input"],
        ["python", "manage.py", "collectstatic", "--no-input"],
    ]

    # Adiciona kafka_setup se existir o management command
    try:
        import subprocess
        result = subprocess.run(
            ["python", "manage.py", "help", "kafka_setup"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            commands.append(["python", "manage.py", "kafka_setup"])
    except Exception:
        logger.debug("Comando kafka_setup não encontrado, pulando...")

    for cmd in commands:
        logger.info(f"Executando: {' '.join(cmd)}")
        try:
            run_django_command(cmd)
        except subprocess.CalledProcessError as e:
            logger.error(f"Falha no comando {' '.join(cmd)}: {e}")
            return e.returncode

    logger.info("Setup do Django concluído!")
    return 0


def run_gunicorn():
    """
    Inicia servidor Gunicorn com OpenTelemetry.
    """
    logger.info("Iniciando Gunicorn com instrumentação OpenTelemetry...")
    logger.info(f"Serviço: {os.getenv('OTEL_SERVICE_NAME', 'django-service')}")
    logger.info(f"Endpoint: {os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'console')}")
    logger.info(f"Ambiente: {os.getenv('APP_ENVIRONMENT', 'production')}")

    # Executa setup do Django antes de iniciar o servidor
    setup_result = setup_django()
    if setup_result != 0:
        logger.error("Falha no setup do Django")
        return setup_result

    # Comando Gunicorn
    gunicorn_cmd = ["gunicorn", "conf.asgi:application", "-c", "gunicorn.config.py"]
    return run_django_command(gunicorn_cmd)


def main():
    """
    Função principal do entrypoint.
    """
    # Configura logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Configura variáveis de ambiente do OpenTelemetry
    setup_opentelemetry_env()

    # Verifica o comando passado
    if len(sys.argv) < 2:
        print("Comandos disponíveis:")
        print("  gunicorn                  - Inicia servidor Gunicorn com OpenTelemetry (inclui setup Django)")
        print("  server                    - Inicia servidor Gunicorn sem setup Django")
        print("  setup                     - Executa apenas setup Django (migrations, collectstatic, kafka)")
        print("  manage.py [args]         - Executa comandos de management do Django")
        print("  python [script] [args]   - Executa scripts Python com OpenTelemetry")
        print("")
        print("Variáveis de ambiente:")
        print("  SKIP_DJANGO_SETUP=true   - Pula setup Django ao usar comando 'gunicorn'")
        print("")
        print("Exemplos:")
        print("  entrypoint.sh gunicorn")
        print("  entrypoint.sh server                # Inicia sem setup")
        print("  entrypoint.sh setup")
        print("  entrypoint.sh manage.py runserver")
        print("  entrypoint.sh manage.py migrate")
        print("  entrypoint.sh python manage.py shell")
        return 1

    command = sys.argv[1]
    
    if command == "gunicorn":
        return run_gunicorn()
    elif command == "server":
        os.environ["SKIP_DJANGO_SETUP"] = "true"
        return run_gunicorn()
    elif command == "setup":
        return setup_django()
    elif command == "manage.py":
        if len(sys.argv) < 3:
            logger.error("Comando manage.py requer argumentos")
            return 1
        cmd_args = ["python", "manage.py"] + sys.argv[2:]
        return run_django_command(cmd_args)
    elif command == "python":
        if len(sys.argv) < 3:
            logger.error("Comando python requer argumentos")
            return 1
        cmd_args = sys.argv[1:]
        return run_django_command(cmd_args)
    else:
        logger.error(f"Comando desconhecido: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())