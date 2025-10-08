# Django Coralogix OpenTelemetry - Guia de Instalação

## Problema Resolvido

Este pacote foi corrigido para funcionar perfeitamente tanto com `opentelemetry-instrument` quanto com configuração manual, resolvendo o erro:

```
django.core.exceptions.ImproperlyConfigured: settings.DATABASES is improperly configured
```

## Instalação

### 1. Adicionar ao projeto Django

```python
# settings.py
INSTALLED_APPS = [
    # ... outros apps
    'django_coralogix_otel',
    # ... outros apps
]

MIDDLEWARE = [
    'django_coralogix_otel.middleware.TraceMiddleware',
    # ... outros middlewares
]
```

### 2. Configurar logging (opcional)

```python
# settings.py - no final do arquivo
from django_coralogix_otel.logging_config import get_logging_config

LOGGING = get_logging_config()
```

## Modos de Uso

### Modo 1: Com `opentelemetry-instrument` (Recomendado para Produção)

```bash
# No container/deployment
opentelemetry-instrument python manage.py showmigrations
opentelemetry-instrument python manage.py runserver
opentelemetry-instrument gunicorn myproject.wsgi:application
```

### Modo 2: Com script wrapper

```bash
# Usando o script fornecido
django-coralogix-otel-run python manage.py showmigrations
django-coralogix-otel-run python manage.py runserver
django-coralogix-otel-run gunicorn myproject.wsgi:application
```

### Modo 3: Configuração Manual (Para desenvolvimento)

```python
# settings.py - sem opentelemetry-instrument
# O pacote configura automaticamente quando não detecta auto-instrumentação
```

## Variáveis de Ambiente

```bash
# Obrigatórias para produção
export OTEL_SERVICE_NAME="my-django-app"
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"

# Opcionais
export OTEL_RESOURCE_ATTRIBUTES="cx.application.name=my-app,cx.subsystem.name=backend"
export APP_ENVIRONMENT="production"
```

## Deploy Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-django-app
spec:
  template:
    spec:
      containers:
        - name: app
          image: my-django-app:latest
          env:
            - name: OTEL_SERVICE_NAME
              value: "my-django-app"
            - name: OTEL_RESOURCE_ATTRIBUTES
              value: "cx.application.name=my-app,cx.subsystem.name=backend"
            - name: OTEL_EXPORTER_OTLP_ENDPOINT
              value: "http://$(OTEL_IP):4317"
            - name: OTEL_PYTHON_DJANGO_INSTRUMENT
              value: "true"
            - name: OTEL_PYTHON_PSYCOPG2_INSTRUMENT
              value: "true"
            - name: OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED
              value: "true"
          envFrom:
            - configMapRef:
                name: my-app-config
          command: ["django-coralogix-otel-run", "gunicorn", "myproject.wsgi:application"]
```

## Troubleshooting

### Erro: "Unknown command" com opentelemetry-instrument

**Solução**: O pacote agora detecta e evita conflitos. Use sempre o comando completo:

```bash
# ✅ Funciona
opentelemetry-instrument python manage.py showmigrations

# ❌ Pode falhar
opentelemetry-instrument python manage.py
```

### Erro: Database connection issues

**Solução**: Verifique se as variáveis de ambiente do banco estão disponíveis:

```bash
# No container
env | grep POSTGRES

# Teste sem OpenTelemetry primeiro
python manage.py showmigrations

# Depois com OpenTelemetry
opentelemetry-instrument python manage.py showmigrations
```

### Desabilitar temporariamente

```bash
# Para testes sem OpenTelemetry
unset OTEL_PYTHON_INSTRUMENTATION_ENABLED
python manage.py showmigrations
```

## Como o Pacote Funciona

1. **Detecção automática**: Detecta se `opentelemetry-instrument` está ativo
2. **Configuração condicional**: Só configura manualmente se não houver auto-instrumentação
3. **Tratamento de erros**: Nunca quebra a inicialização do Django
4. **Compatibilidade**: Funciona com todos os comandos Django
5. **Logging estruturado**: JSON com trace context em ambos os modos

## Exemplo Completo

```python
# settings.py
import os

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django_coralogix_otel',  # Adicionar o app
    # ... outros apps
]

MIDDLEWARE = [
    'django_coralogix_otel.middleware.TraceMiddleware',  # Adicionar o middleware
    # ... outros middlewares
]

# No final do arquivo
from django_coralogix_otel.logging_config import get_logging_config
LOGGING = get_logging_config()
```

```bash
# No terminal/container
export OTEL_SERVICE_NAME="my-app"
export OTEL_EXPORTER_OTLP_ENDPOINT="http://otel-collector:4317"

# Testar
opentelemetry-instrument python manage.py showmigrations
opentelemetry-instrument python manage.py runserver
```

O pacote agora é robusto e funciona em qualquer cenário!