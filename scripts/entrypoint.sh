#!/bin/bash

# entrypoint.sh
# Script para inicializar aplicações Django com OpenTelemetry auto-instrumentation
# Compatível com django-coralogix-otel e estratégia híbrida

set -e

echo "=== Django Coralogix OpenTelemetry Entrypoint ==="
echo "Starting Django application with OpenTelemetry instrumentation..."

# Verificar se as variáveis de ambiente necessárias estão definidas
if [ -z "$OTEL_SERVICE_NAME" ]; then
    echo "Warning: OTEL_SERVICE_NAME not set, using default 'django-app'"
    export OTEL_SERVICE_NAME="django-app"
fi

if [ -z "$OTEL_EXPORTER_OTLP_ENDPOINT" ]; then
    echo "Warning: OTEL_EXPORTER_OTLP_ENDPOINT not set"
fi

# Configurar auto-instrumentação para estratégia híbrida
export OTEL_PYTHON_INSTRUMENTATION_ENABLED=true
export DJANGO_CORALOGIX_AUTO_INIT=true

# Habilitar instrumentações específicas baseadas na estratégia híbrida
export OTEL_PYTHON_DJANGO_INSTRUMENT=true
export OTEL_PYTHON_REQUESTS_INSTRUMENT=true
export OTEL_PYTHON_PSYCOPG2_INSTRUMENT=true
export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
export OTEL_PYTHON_WSGI_INSTRUMENT=true
export OTEL_PYTHON_ASGI_INSTRUMENT=true

# Configurações adicionais do OpenTelemetry
export OTEL_TRACES_EXPORTER=otlp
export OTEL_METRICS_EXPORTER=otlp
export OTEL_LOGS_EXPORTER=otlp

# Propagators
export OTEL_PROPAGATORS=tracecontext,baggage

# Configurar sampling (ajuste conforme necessário)
export OTEL_TRACES_SAMPLER=always_on
# Para produção, considere usar: export OTEL_TRACES_SAMPLER=traceidratio
# export OTEL_TRACES_SAMPLER_ARG=0.1  # 10% sampling

# Configurações de batch para melhor performance
export OTEL_BSP_SCHEDULE_DELAY=5000  # 5 segundos
export OTEL_BSP_MAX_QUEUE_SIZE=2048
export OTEL_BSP_MAX_EXPORT_BATCH_SIZE=512
export OTEL_BSP_EXPORT_TIMEOUT=30000  # 30 segundos

# Configurações de métricas
export OTEL_METRIC_EXPORT_INTERVAL=30000  # 30 segundos

# Se for desenvolvimento local, usar console exporter
if [ "$APP_ENVIRONMENT" = "local" ] || [ "$DJANGO_DEBUG" = "True" ] || [ "$OTEL_LOG_LEVEL" = "DEBUG" ]; then
    echo "Local development detected, enabling console exporters"
    export OTEL_TRACES_EXPORTER=console,otlp
    export OTEL_METRICS_EXPORTER=console,otlp
    export OTEL_LOGS_EXPORTER=console,otlp
fi

# Função para setup inicial do Django
setup_django() {
    echo "=== Django Setup ==="

    # Permitir pular o setup se a variável SKIP_DJANGO_SETUP estiver definida
    if [ "$SKIP_DJANGO_SETUP" = "true" ]; then
        echo "Skipping Django setup (SKIP_DJANGO_SETUP=true)"
        return 0
    fi

    echo "Running Database Migrations..."
    opentelemetry-instrument python manage.py migrate --no-input

    echo "Running CollectStatic..."
    opentelemetry-instrument python manage.py collectstatic --no-input

    # Setup adicional opcional (kafka, etc.)
    if [ -n "$DJANGO_EXTRA_SETUP_COMMANDS" ]; then
        echo "Running extra setup commands..."
        IFS=',' read -ra COMMANDS <<< "$DJANGO_EXTRA_SETUP_COMMANDS"
        for cmd in "${COMMANDS[@]}"; do
            echo "Executing: $cmd"
            opentelemetry-instrument python manage.py $cmd
        done
    fi

    echo "Django setup completed!"
}

# Função para executar comandos Django com estratégia híbrida
run_django_command() {
    echo "Executing: opentelemetry-instrument $@"
    exec opentelemetry-instrument "$@"
}

# Função para executar com Gunicorn
run_gunicorn() {
    echo "Starting Gunicorn with OpenTelemetry instrumentation..."
    echo "Service: $OTEL_SERVICE_NAME"
    echo "Endpoint: $OTEL_EXPORTER_OTLP_ENDPOINT"
    echo "Environment: $APP_ENVIRONMENT"
    echo "Strategy: Hybrid (auto-instrumentation + manual)"
    echo "Gunicorn Config: $GUNICORN_CONFIG"

    # Executar setup do Django antes de iniciar o servidor
    setup_django

    # Configurar Gunicorn com opções padrão se não especificadas
    if [ -z "$GUNICORN_CONFIG" ]; then
        # Verificar se existe arquivo de configuração do Gunicorn local
        if [ -f "gunicorn.config.py" ]; then
            echo "Using local gunicorn.config.py configuration file"
            export GUNICORN_CONFIG="--config gunicorn.config.py conf.asgi:application"
        else
            # Tentar encontrar o arquivo na biblioteca instalada
            echo "Local gunicorn.config.py not found, searching in django-coralogix-otel library..."
            library_config=$(python -c "
import sys
try:
    from django_coralogix_otel import get_gunicorn_config_path
    config_path = get_gunicorn_config_path()
    if config_path:
        print(config_path)
    else:
        sys.exit(1)
except ImportError:
    sys.stderr.write('django-coralogix-otel not available\n')
    sys.exit(1)
except Exception as e:
    sys.stderr.write(f'Error getting gunicorn config: {e}\n')
    sys.exit(1)
" 2>/dev/null)

            if [ $? -eq 0 ] && [ -n "$library_config" ] && [ -f "$library_config" ]; then
                echo "Using django-coralogix-otel library gunicorn.config.py: $library_config"
                export GUNICORN_CONFIG="--config $library_config conf.asgi:application"
            else
                echo "gunicorn.config.py not found in library, using default Gunicorn configuration"
                export GUNICORN_CONFIG=" conf.asgi:application -b 0.0.0.0:8080 --access-logfile - --error-logfile - --log-level warning -k uvicorn.workers.UvicornWorker"
            fi
        fi
    fi

    exec opentelemetry-instrument gunicorn $GUNICORN_CONFIG
}

# Função para executar com Django Development Server
run_development_server() {
    echo "Starting Django Development Server with OpenTelemetry instrumentation..."
    echo "Service: $OTEL_SERVICE_NAME"
    echo "Environment: Development"
    echo "Strategy: Hybrid (auto-instrumentation + manual)"

    # Executar setup do Django antes de iniciar o servidor
    setup_django

    exec opentelemetry-instrument python manage.py runserver 0.0.0.0:8080
}

# Função para executar com Uvicorn (ASGI)
run_uvicorn() {
    echo "Starting Uvicorn with OpenTelemetry instrumentation..."
    echo "Service: $OTEL_SERVICE_NAME"
    echo "Environment: $APP_ENVIRONMENT"
    echo "Strategy: Hybrid (auto-instrumentation + manual)"

    # Executar setup do Django antes de iniciar o servidor
    setup_django

    # Configurar Uvicorn com opções padrão se não especificadas
    if [ -z "$UVICORN_CONFIG" ]; then
        export UVICORN_CONFIG="--host 0.0.0.0 --port 8080 --workers 4"
    fi

    exec opentelemetry-instrument uvicorn $UVICORN_CONFIG
}

# Função para executar apenas o setup
run_setup_only() {
    echo "Running Django setup only..."
    setup_django
    echo "Setup completed successfully!"
}

# Função para executar comandos customizados
run_custom_command() {
    echo "Executing custom command with OpenTelemetry instrumentation..."
    exec opentelemetry-instrument "$@"
}

# Verificar o comando passado
case "$1" in
    "gunicorn")
        run_gunicorn
        ;;
    "runserver")
        run_development_server
        ;;
    "uvicorn")
        run_uvicorn
        ;;
    "setup")
        # Executar apenas o setup do Django
        run_setup_only
        ;;
    "manage.py")
        shift
        run_django_command python manage.py "$@"
        ;;
    "python")
        run_django_command "$@"
        ;;
    "custom")
        shift
        run_custom_command "$@"
        ;;
    *)
        echo "Available commands:"
        echo "  gunicorn                  - Start Gunicorn server with OpenTelemetry (includes Django setup)"
        echo "  runserver                 - Start Django development server with OpenTelemetry"
        echo "  uvicorn                   - Start Uvicorn server for ASGI applications"
        echo "  setup                     - Run only Django setup (migrations, collectstatic, etc.)"
        echo "  manage.py [args]         - Run Django management commands"
        echo "  python [script] [args]   - Run Python scripts with OpenTelemetry"
        echo "  custom [command] [args]  - Run custom commands with OpenTelemetry"
        echo ""
        echo "Environment variables:"
        echo "  SKIP_DJANGO_SETUP=true   - Skip Django setup when using server commands"
        echo "  DJANGO_EXTRA_SETUP_COMMANDS - Comma-separated list of extra setup commands"
        echo "  GUNICORN_CONFIG          - Custom Gunicorn configuration"
        echo "  UVICORN_CONFIG           - Custom Uvicorn configuration"
        echo "  APP_ENVIRONMENT          - Set to 'local' for console exporters"
        echo ""
        echo "Examples:"
        echo "  $0 gunicorn"
        echo "  $0 runserver"
        echo "  $0 setup"
        echo "  $0 manage.py runserver"
        echo "  $0 manage.py migrate"
        echo "  $0 python manage.py shell"
        echo "  $0 custom python my_script.py"
        echo ""
        echo "Note: This script uses the hybrid strategy from django-coralogix-otel package"
        exit 1
        ;;
esac