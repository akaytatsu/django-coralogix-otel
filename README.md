# Django Coralogix OpenTelemetry

Pacote Django para integração simplificada de OpenTelemetry com Coralogix.

## 🚀 Funcionalidades

- Configuração automática de tracing, métricas e logging
- Integração com Coralogix
- Formatação JSON de logs com trace context
- Instrumentação automática de Django, PostgreSQL, Requests e Kafka
- Configuração simplificada via variáveis de ambiente
- Suporte para desenvolvimento local e produção

## 📦 Instalação

```bash
pip install django-coralogix-otel
```

## 🔧 Configuração

### 1. Adicione ao settings.py do Django:

```python
INSTALLED_APPS = [
    # ... outras apps
    'django_coralogix_otel',
    # ... outras apps
]

# Importe a configuração de logging
from django_coralogix_otel.logging_config import LOGGING_CONFIG
LOGGING = LOGGING_CONFIG
```

### 2. Configure as variáveis de ambiente:

```bash
# Coralogix
OTEL_EXPORTER_OTLP_ENDPOINT=https://ingress.coralogix.com:443
OTEL_EXPORTER_OTLP_HEADERS=Authorization=Bearer YOUR_CORALOGIX_API_KEY

# Service
OTEL_SERVICE_NAME=seu-servico
OTEL_SERVICE_VERSION=1.0.0
APP_ENVIRONMENT=production
```

### 3. Use o script de inicialização (opcional):

```bash
# Crie um script entrypoint.sh semelhante a:
#!/bin/bash
exec django-coralogix-otel-run gunicorn seu_projeto.wsgi:application
```

## 📋 Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `OTEL_SERVICE_NAME` | Nome do serviço | `django-service` |
| `OTEL_SERVICE_VERSION` | Versão do serviço | `1.0.0` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Endpoint Coralogix | - |
| `OTEL_EXPORTER_OTLP_HEADERS` | Headers de autenticação | - |
| `APP_ENVIRONMENT` | Ambiente (local/production) | `local` |
| `OTEL_TRACES_SAMPLER_ARG` | Taxa de amostragem | `1.0` |

## 🎯 Uso Avançado

### Configuração Personalizada

```python
# settings.py
DJANGO_CORALOGIX_OTEL = {
    'SERVICE_NAME': 'meu-servico',
    'SERVICE_VERSION': '2.0.0',
    'ENABLE_KAFKA_INSTRUMENTATION': True,
    'CUSTOM_RESOURCE_ATTRIBUTES': {
        'team': 'backend',
        'cost_center': 'engineering',
    }
}
```

### Middleware Personalizado

```python
# Adicione middleware customizado se necessário
MIDDLEWARE = [
    'django_coralogix_otel.middleware.TraceMiddleware',
    # ... outros middlewares
]
```

## 🛠️ Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/django-coralogix-otel.git
cd django-coralogix-otel

# Instale em modo de desenvolvimento
pip install -e .[dev]

# Execute os testes
pytest

# Formate o código
black .
isort .
flake8 .
```

## 📄 Licença

MIT License

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor, abra uma issue ou envie um pull request.