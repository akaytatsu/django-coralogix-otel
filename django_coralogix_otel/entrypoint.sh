#!/bin/bash
# Entrypoint script para Django Coralogix OpenTelemetry

set -e

# Importa e executa o módulo Python
python -c "import django_coralogix_otel.entrypoint; django_coralogix_otel.entrypoint.main()" "$@"