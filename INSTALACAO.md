# Guia Prático de Instalação - django-coralogix-otel

Este guia fornece instruções práticas e diretas para instalar e configurar o pacote `django-coralogix-otel` em projetos Django.

## 📋 Pré-requisitos

- Python 3.7+
- Django 3.2+
- Acesso ao Coralogix (chave privada e endpoint)

## 🚀 Instalação Rápida

### 1. Instalar o pacote

```bash
pip install django-coralogix-otel
```

### 2. Configurar variáveis de ambiente obrigatórias

```bash
# Chave privada do Coralogix
export CORALOGIX_PRIVATE_KEY="sua-chave-privada-aqui"

# Endpoint OTLP do Coralogix
export OTEL_EXPORTER_OTLP_ENDPOINT="https://ingress.coralogix.com:443"
```

### 3. Configurar variáveis de ambiente opcionais

```bash
# Identificação do serviço
export OTEL_SERVICE_NAME="meu-app-django"
export CORALOGIX_APPLICATION_NAME="minha-aplicacao"
export CORALOGIX_SUBSYSTEM_NAME="backend"

# Ambiente
export OTEL_DEPLOYMENT_ENVIRONMENT="production"

# Instrumentações (habilitar/desabilitar)
export OTEL_PYTHON_DJANGO_INSTRUMENT="true"
export OTEL_PYTHON_REQUESTS_INSTRUMENT="true"
export OTEL_PYTHON_PSYCOPG2_INSTRUMENT="true"
export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED="true"
```

## ⚙️ Configuração do Django

### 1. Adicionar middleware no settings.py

```python
# settings.py

MIDDLEWARE = [
    'django_coralogix_otel.middleware.OpenTelemetryMiddleware',  # Adicionar no início
    # ... outros middlewares
]
```

**IMPORTANTE:** O pacote NÃO precisa ser adicionado ao `INSTALLED_APPS`.

### 2. Inicializar no wsgi.py (produção)

```python
# wsgi.py
import os
from django_coralogix_otel import initialize_opentelemetry

# Inicializar OpenTelemetry antes da aplicação
initialize_opentelemetry()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meuprojeto.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 3. Inicializar no asgi.py (ASGI)

```python
# asgi.py
import os
from django_coralogix_otel import initialize_opentelemetry

# Inicializar OpenTelemetry antes da aplicação
initialize_opentelemetry()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meuprojeto.settings')
from django.core.asgi import get_asgi_application
application = get_asgi_application()
```

## 🐳 Configuração para Docker/Kubernetes

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Variáveis de ambiente para produção
ENV DJANGO_CORALOGIX_AUTO_INIT=true
ENV OTEL_LOG_LEVEL=INFO
ENV DJANGO_DEBUG=False

EXPOSE 8000

CMD ["gunicorn", "meuprojeto.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### ConfigMap para Kubernetes

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: django-opentelemetry
data:
  OTEL_SERVICE_NAME: "meu-app-django"
  OTEL_EXPORTER_OTLP_ENDPOINT: "https://ingress.coralogix.com:443"
  OTEL_PYTHON_DJANGO_INSTRUMENT: "true"
  OTEL_PYTHON_REQUESTS_INSTRUMENT: "true"
  OTEL_PYTHON_PSYCOPG2_INSTRUMENT: "true"
  OTEL_DEPLOYMENT_ENVIRONMENT: "production"
  CORALOGIX_APPLICATION_NAME: "minha-aplicacao"
  CORALOGIX_SUBSYSTEM_NAME: "backend"
```

### Secret para Kubernetes

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: coralogix-secret
type: Opaque
data:
  CORALOGIX_PRIVATE_KEY: <base64-encoded-key>
```

## 🔧 Configuração para Desenvolvimento

### Variáveis de ambiente para desenvolvimento

```bash
export CORALOGIX_PRIVATE_KEY="dev-key"
export OTEL_EXPORTER_OTLP_ENDPOINT="https://ingress.coralogix.com:443"
export OTEL_SERVICE_NAME="meuapp-dev"
export OTEL_LOG_LEVEL=DEBUG
export DJANGO_DEBUG=True
export DJANGO_CORALOGIX_AUTO_INIT=true
```

### Inicialização com console exporter

```python
# wsgi.py (desenvolvimento)
from django_coralogix_otel import initialize_opentelemetry

# Habilitar console exporter para ver traces no terminal
initialize_opentelemetry(enable_console_exporter=True)
```

## ✅ Verificação da Instalação

### 1. Testar inicialização

```python
# test_installation.py
from django_coralogix_otel import get_initialization_status

if get_initialization_status():
    print("✅ OpenTelemetry configurado com sucesso")
else:
    print("❌ OpenTelemetry não está configurado")
```

### 2. Verificar instrumentações habilitadas

```python
from django_coralogix_otel import get_enabled_instrumentations

print(f"Instrumentações habilitadas: {get_enabled_instrumentations()}")
```

### 3. Testar com servidor de desenvolvimento

```bash
python manage.py runserver
```

Verifique os logs para confirmar que o OpenTelemetry foi inicializado.

## 🚨 Solução de Problemas Comuns

### OpenTelemetry não inicializa
- Verifique se `CORALOGIX_PRIVATE_KEY` está definida
- Confirme que `OTEL_EXPORTER_OTLP_ENDPOINT` é válido
- Verifique logs para erros de importação

### Traces não aparecem no Coralogix
- Confirme as credenciais do Coralogix
- Teste com `enable_console_exporter=True` para desenvolvimento
- Verifique se o endpoint OTLP está correto

### Instrumentações específicas não funcionam
- Verifique variáveis `OTEL_PYTHON_*_INSTRUMENT`
- Confirme se as dependências estão instaladas

## 📝 Resumo das Etapas Essenciais

1. **Instalar pacote**: `pip install django-coralogix-otel`
2. **Configurar variáveis**: `CORALOGIX_PRIVATE_KEY` e `OTEL_EXPORTER_OTLP_ENDPOINT`
3. **Adicionar middleware**: No início da lista `MIDDLEWARE` no `settings.py`
4. **Inicializar**: Chamar `initialize_opentelemetry()` no `wsgi.py`/`asgi.py`
5. **Verificar**: Testar com `get_initialization_status()`

**Lembrete:** O pacote funciona via middleware e configuração, NÃO é necessário adicionar ao `INSTALLED_APPS`.