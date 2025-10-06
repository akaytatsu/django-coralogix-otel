# Django Coralogix OpenTelemetry - Solução para Erro de Logging

## Problema
O erro `Unable to configure formatter 'json_with_trace'` ocorre devido a problemas na importação do formatter customizado durante a configuração do logging do Django, especialmente em ambientes com diferentes versões (Django 3.2 e 5.2).

## Solução Implementada

### 1. Abordagem Simplificada
Criamos um novo módulo `simple_logging.py` com uma abordagem mais direta e robusta:

```python
from django_coralogix_otel.simple_logging import setup_json_logging
setup_json_logging()
```

### 2. Formatters em Múltiplos Módulos
- `logging_config.py`: Contém o formatter principal para uso via configuração
- `otel_config.py`: Contém um formatter de fallback
- `simple_logging.py`: Contém uma implementação independente

### 3. Configuração Automática
A configuração agora tenta múltiplas abordagens em ordem de preferência:

1. **Simplificada**: Usa `simple_logging.setup_json_logging()`
2. **Django Config**: Tenta configurar via `settings.LOGGING`
3. **Fallback Direto**: Configura o logger raiz diretamente

## Uso Recomendado

### Para Django 3.2 e 5.2
No seu `settings.py`, remova a configuração manual de LOGGING e deixe o pacote configurar automaticamente:

```python
# Adicione ao INSTALLED_APPS
INSTALLED_APPS = [
    # ... outros apps
    'django_coralogix_otel',
    # ... outros apps
]

# Opcional: configurar variáveis de ambiente
import os
os.environ.setdefault('DJANGO_CORALOGIX_OTEL', 'enabled')
```

### Para Configuração Manual
Se precisar de configuração manual:

```python
# Em settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json_with_trace': {
            '()': 'django_coralogix_otel.simple_logging.JSONFormatterWithTrace',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json_with_trace',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## Variáveis de Ambiente Suportadas

- `LOG_LEVEL`: Nível de log (INFO, DEBUG, WARNING, ERROR)
- `APP_ENVIRONMENT`: Ambiente (local, staging, production)
- `OTEL_PYTHON_INSTRUMENTATION_ENABLED`: Ativa auto-instrumentação

## Compatibilidade

- ✅ Django 3.2
- ✅ Django 5.2
- ✅ Python 3.8+
- ✅ OpenTelemetry SDK

## Debug

Para habilitar logs de debug do pacote:

```python
import logging
logging.getLogger('django_coralogix_otel').setLevel('DEBUG')
```