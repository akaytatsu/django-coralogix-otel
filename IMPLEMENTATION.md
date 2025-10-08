# Django Coralogix OpenTelemetry

Este pacote fornece uma integração simplificada entre Django e OpenTelemetry com envio para Coralogix.

## Estrutura do Pacote

```
django-coralogix-otel/
├── django_coralogix_otel/
│   ├── __init__.py              # Configuração principal
│   ├── apps.py                  # Django AppConfig
│   ├── otel_config.py           # Configuração OpenTelemetry
│   ├── logging_config.py        # Configuração de logging
│   ├── middleware.py            # Middleware para trace context
│   └── management/
│       └── commands/
│           └── otel_run.py      # Management command
├── scripts/
│   └── django-coralogix-otel-run # Script de inicialização
├── example_settings.py          # Exemplo de configuração
├── .env.example                 # Exemplo de variáveis de ambiente
├── README.md                    # Documentação
├── setup.py                     # Setup tradicional
├── pyproject.toml              # Setup moderno
└── requirements.txt            # Dependências
```

## Como Funciona

1. **Auto-configuração**: O pacote configura automaticamente OpenTelemetry quando o Django inicia
2. **Instrumentação**: Habilita tracing para Django, PostgreSQL, Requests e Kafka
3. **Logging**: Configura logs estruturados em JSON com trace context
4. **Coralogix**: Envia traces, métricas e logs para o Coralogix
5. **Flexibilidade**: Permite customização via settings do Django

## Principais Componentes

### 1. AppConfig (`apps.py`)
- Inicia a configuração do OpenTelemetry quando o Django está pronto
- Verifica se já não foi configurado por auto-instrumentação

### 2. OpenTelemetry Config (`otel_config.py`)
- Configura providers de trace e métricas
- Setup de exporters (OTLP para produção, console para dev)
- Instrumentação automática de bibliotecas
- Formatter JSON para logs com trace context

### 3. Logging Config (`logging_config.py`)
- Configuração de logging Django com formatter personalizado
- Suporte para loggers customizados via settings
- Detecção automática de ambiente local vs produção

### 4. Middleware (`middleware.py`)
- Adiciona contexto específico da requisição aos spans
- Informações de usuário, session, HTTP headers
- Métricas de response time e status codes

### 5. Management Command (`otel_run.py`)
- Permite executar comandos Django com instrumentação
- Wrapper around `opentelemetry-instrument`

### 6. Script (`django-coralogix-otel-run`)
- Script bash para inicialização da aplicação
- Configura todas as variáveis de ambiente necessárias
- Suporte para diferentes comandos (gunicorn, manage.py, etc.)

## Vantagens

1. **Padronização**: Mesma configuração para todos os projetos Django
2. **Simplicidade**: Configuração mínima necessária
3. **Flexibilidade**: Altamente customizável via settings
4. **Performance**: Configurações otimizadas para produção
5. **Debugging**: Facilita debugging com trace context completo

## Próximos Passos

1. Publicar no PyPI
2. Criar documentação detalhada
3. Adicionar testes automatizados
4. Suporte para outras bibliotecas (Redis, Celery, etc.)
5. Integração com CI/CD pipelines