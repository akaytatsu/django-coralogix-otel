#!/bin/bash
# setup_gunicorn_config.sh
# Script para copiar gunicorn.config.py da lib django-coralogix-otel durante o build do Docker

set -e

echo "Setting up gunicorn.config.py from django-coralogix-otel..."

# Verificar se já existe o arquivo localmente
if [ -f "gunicorn.config.py" ]; then
    echo "gunicorn.config.py already exists in project root, skipping copy."
    exit 0
fi

# Tentar obter o caminho da lib
config_path=$(python -c "
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

if [ $? -eq 0 ] && [ -n "$config_path" ] && [ -f "$config_path" ]; then
    echo "Copying gunicorn.config.py from: $config_path"
    cp "$config_path" .
    echo "✅ gunicorn.config.py copied successfully!"
else
    echo "❌ Failed to find gunicorn.config.py in django-coralogix-otel"
    exit 1
fi