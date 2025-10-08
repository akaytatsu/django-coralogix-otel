
# Django Coralogix OpenTelemetry

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-3.2+-green.svg)](https://www.djangoproject.com/)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-1.0+-orange.svg)](https://opentelemetry.io/)

Um pacote Python para auto-instrumentação OpenTelemetry com Coralogix para aplicações Django. Implementa estratégia híbrida (auto-instrumentação + configuração manual) com suporte completo às variáveis de ambiente do Kubernetes.

## 🚀 Características

- **Instrumentação Automática**: Tracing, métricas e logging para Django e bibliotecas comuns
- **Estratégia Híbrida**: Combina auto-instrumentação com configuração manual
- **Suporte Kubernetes**: Compatível com variáveis de ambiente padrão do Kubernetes
- **Atributos Coralogix**: Atributos customizados `cx.application.name` e `cx.subsystem.name`
- **Configuração Gunicorn Automática**: Referência automática ao gunicorn.config.py otimizado
- **Fallbacks Robusto**: Continua funcionando mesmo sem OpenTelemetry disponível
- **Desenvolvimento & Produção**: Suporte a exportadores console (dev) e OTLP (prod)
- **Instrumentações Suportadas**: Django, PostgreSQL, Requests, Logging, WSGI/ASGI, Kafka

## 📦 Instalação

### Instalação via pip

```bash
pip install django-coralogix-otel
```

### Instalação com dependências opcionais

```bash
# Com suporte a Kafka
pip install django-coralogix-otel[kafka]

# Para desenvolvimento
pip install django-coralogix-otel[dev]

# Para documentação
pip install django-coralogix-otel[docs]
```

### Dependências

O pacote requer as seguintes dependências principais:

```bash
pip install opentelemetry-sdk opentelemetry-exporter-otlp Django>=3.2
```

## ⚙️ Configuração Rápida

### 1. Configuração no settings.py

```python
# settings.py
from django_coralogix_otel import configure_django_settings

# Adicionar configurações automáticas
otel_settings = configure_django_settings()

# Adicionar middleware OpenTelemetry no início da lista
MIDDLEWARE = otel_settings['MIDDLEWARE'] + MIDDLEWARE

# Adicionar configurações de logging (se disponível)
if 'LOGGING' in otel_settings:
    LOGGING = otel_settings['LOGGING']
```

### 2. Configuração no wsgi.py

```python
# wsgi.py
import os
from django_coralogix_otel import initialize_opentelemetry

# Inicializar OpenTelemetry antes da aplicação
initialize_opentelemetry()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 3. Configuração no asgi.py

```python
# asgi.py
import os
from django_coralogix_otel import initialize_opentelemetry

# Inicializar OpenTelemetry antes da aplicação
initialize_opentelemetry()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
from django.core.asgi import get_asgi_application
application = get_asgi_application()
```

## 🔧 Variáveis de Ambiente

### Variáveis Obrigatórias

```bash
# Chave privada do Coralogix
CORALOGIX_PRIVATE_KEY=your-private-key

# Endpoint OTLP do Coralogix
OTEL_EXPORTER_OTLP_ENDPOINT=https://ingress.coralogix.com:443
```

### Variáveis Opcionais com Valores Padrão

```bash
# Identificação do serviço
OTEL_SERVICE_NAME=my-django-app
CORALOGIX_APPLICATION_NAME=my-application
CORALOGIX_SUBSYSTEM_NAME=backend
OTEL_SERVICE_NAMESPACE=default
OTEL_SERVICE_VERSION=1.0.0

# Ambiente
OTEL_DEPLOYMENT_ENVIRONMENT=production

# Configurações de instrumentação
OTEL_PYTHON_DJANGO_INSTRUMENT=true
OTEL_PYTHON_REQUESTS_INSTRUMENT=true
OTEL_PYTHON_PSYCOPG2_INSTRUMENT=true
OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
OTEL_PYTHON_KAFKA_INSTRUMENT=false
OTEL_PYTHON_WSGI_INSTRUMENT=true
OTEL_PYTHON_ASGI_INSTRUMENT=true

# Inicialização automática
DJANGO_CORALOGIX_AUTO_INIT=true

# Debug e desenvolvimento
OTEL_LOG_LEVEL=INFO
DJANGO_DEBUG=False
```

### Variáveis do Kubernetes

```bash
# Atributos de resource do Kubernetes
OTEL_RESOURCE_ATTRIBUTES=k8s.namespace=production,k8s.pod.name=$(POD_NAME),k8s.deployment.name=myapp

# Configurações específicas do cluster
KUBERNETES_SERVICE_HOST=10.0.0.1
KUBERNETES_SERVICE_PORT=443
```

## 🎯 Uso Avançado

### Estratégia Híbrida

```python
from django_coralogix_otel import hybrid_instrumentation

# Aplicar instrumentação híbrida após inicialização do Django
hybrid_instrumentation()
```

### Instrumentação Manual

```python
from django_coralogix_otel import get_tracer

def minha_view(request):
    tracer = get_tracer("minhaapp.views")

    with tracer.start_as_current_span("processar_dados") as span:
        span.set_attribute("user.id", request.user.id)
        span.set_attribute("operation.type", "data_processing")

        # Sua lógica de negócio aqui
        data = process_data(request.data)

        span.set_attribute("result.size", len(data))
        return JsonResponse(data)
```

### Configuração para Desenvolvimento

```python
# Para desenvolvimento local com console exporter
from django_coralogix_otel import initialize_opentelemetry

# Habilitar console exporter para ver traces no terminal
initialize_opentelemetry(enable_console_exporter=True)
```

## 🚀 Integração com Kubernetes

### ConfigMap para Kubernetes

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: django-opentelemetry
data:
  OTEL_SERVICE_NAME: "my-django-app"
  OTEL_RESOURCE_ATTRIBUTES: "k8s.namespace=production,k8s.pod.name=$(POD_NAME)"
  OTEL_EXPORTER_OTLP_ENDPOINT: "https://ingress.coralogix.com:443"
  OTEL_PYTHON_DJANGO_INSTRUMENT: "true"
  OTEL_PYTHON_REQUESTS_INSTRUMENT: "true"
  OTEL_PYTHON_PSYCOPG2_INSTRUMENT: "true"
  OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED: "true"
  OTEL_DEPLOYMENT_ENVIRONMENT: "production"
  CORALOGIX_APPLICATION_NAME: "my-application"
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

### Deployment com Sidecar (Opcional)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-app
spec:
  template:
    spec:
      containers:
      - name: django-app
        image: my-django-app:latest
        envFrom:
        - configMapRef:
            name: django-opentelemetry
        - secretRef:
            name: coralogix-secret
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
```

## 📊 Instrumentações Suportadas

### Django Framework
- **Requests HTTP**: Tracing automático de todas as requisições
- **Views**: Instrumentação de views e métodos
- **Templates**: Timing de renderização de templates
- **Middleware**: Middleware customizado com atributos Coralogix

### Banco de Dados
- **PostgreSQL**: Queries via psycopg2 com tracing de SQL
- **Query Performance**: Métricas de tempo de execução de queries

### HTTP Clients
- **Requests**: Tracing de requisições HTTP externas
- **HTTP Headers**: Propagação de contexto entre serviços

### Logging
- **Logs Estruturados**: Integração com logging do Python
- **Correlação**: Logs correlacionados com traces
- **Níveis**: Suporte a todos os níveis de log

### Mensageria
- **Kafka**: Produção e consumo de mensagens (opcional)
- **Tópicos**: Tracing por tópico e partição

### Servidores Web
- **WSGI**: Instrumentação para servidores WSGI (Gunicorn, uWSGI)
- **ASGI**: Suporte para servidores ASGI (Daphne, Uvicorn)

## 🔧 API Reference

### Funções Principais

#### `initialize_opentelemetry(enable_console_exporter=False)`
Inicializa o OpenTelemetry com estratégia híbrida.

**Parâmetros:**
- `enable_console_exporter`: Habilita exportador console para desenvolvimento

**Retorna:**
- `bool`: True se a inicialização foi bem-sucedida

#### `hybrid_instrumentation()`
Aplica instrumentação híbrida (auto + manual).

**Retorna:**
- `bool`: True se a instrumentação foi aplicada com sucesso

#### `safe_configure_opentelemetry()`
Configuração segura com fallbacks robustos.

**Retorna:**
- `bool`: True se a configuração foi bem-sucedida

#### `configure_django_settings()`
Retorna configurações para settings.py do Django.

**Retorna:**
- `Dict[str, Any]`: Configurações para MIDDLEWARE e LOGGING

### Utilitários

#### `validate_environment_variables()`
Valida variáveis de ambiente necessárias.

**Retorna:**
- `bool`: True se todas as variáveis necessárias estão presentes

#### `get_enabled_instrumentations()`
Retorna lista de instrumentações habilitadas.

**Retorna:**
- `List[str]`: Lista de instrumentações habilitadas

#### `is_instrumentation_enabled(name)`
Verifica se uma instrumentação está habilitada.

**Parâmetros:**
- `name`: Nome da instrumentação (django, requests, etc.)

**Retorna:**
- `bool`: True se a instrumentação está habilitada

#### `get_otel_config()`
Retorna configuração OpenTelemetry atual.

**Retorna:**
- `Dict[str, Any]`: Configuração completa do OpenTelemetry

### Middleware

#### `OpenTelemetryMiddleware`
Middleware Django para tracing automático com atributos Coralogix.

**Atributos Incluídos:**
- Atributos HTTP padrão (method, URL, status code)
- Atributos Coralogix (application.name, subsystem.name)
- Atributos Django (view_name, user, session)
- Informações de performance (duration, response size)

## 🛠️ Desenvolvimento

### Configuração para Desenvolvimento Local

```bash
# Variáveis de ambiente para desenvolvimento
export CORALOGIX_PRIVATE_KEY=dev-key
export OTEL_EXPORTER_OTLP_ENDPOINT=https://ingress.coralogix.com:443
export OTEL_SERVICE_NAME=myapp-dev
export OTEL_LOG_LEVEL=DEBUG
export DJANGO_DEBUG=True
export DJANGO_CORALOGIX_AUTO_INIT=true
```

### Testando Localmente

```python
# test_instrumentation.py
from django_coralogix_otel import (
    initialize_opentelemetry,
    get_initialization_status,
    get_enabled_instrumentations
)

# Inicializar com console exporter para desenvolvimento
initialize_opentelemetry(enable_console_exporter=True)

if get_initialization_status():
    print("✅ OpenTelemetry configurado com sucesso")
    print(f"📊 Instrumentações habilitadas: {get_enabled_instrumentations()}")
else:
    print("❌ Falha na configuração OpenTelemetry")
```

### Executando com Django Development Server

```bash
# Configurar variáveis de ambiente
export DJANGO_CORALOGIX_AUTO_INIT=true
export OTEL_LOG_LEVEL=DEBUG

# Executar servidor de desenvolvimento
python manage.py runserver
```

## 🔍 Troubleshooting

### Verificar Status da Instrumentação

```python
from django_coralogix_otel import get_initialization_status

if get_initialization_status():
    print("✅ OpenTelemetry ativo e instrumentando")
else:
    print("❌ OpenTelemetry inativo ou com problemas")
```

### Logs de Depuração

```python
import logging

# Habilitar logs detalhados do pacote
logging.getLogger('django_coralogix_otel').setLevel(logging.DEBUG)

# Ver logs no console
logging.basicConfig(level=logging.DEBUG)
```

### Validação de Variáveis de Ambiente

```python
from django_coralogix_otel import validate_environment_variables

if not validate_environment_variables():
    print("❌ Verifique as variáveis de ambiente obrigatórias")
    # Lista de variáveis obrigatórias:
    # - CORALOGIX_PRIVATE_KEY
    # - OTEL_EXPORTER_OTLP_ENDPOINT
else:
    print("✅ Variáveis de ambiente validadas com sucesso")
```

### Problemas Comuns

1. **OpenTelemetry não inicializa**
   - Verifique se `CORALOGIX_PRIVATE_KEY` está definida
   - Confirme que `OTEL_EXPORTER_OTLP_ENDPOINT` é válido
   - Verifique logs para erros de importação

2. **Traces não aparecem no Coralogix**
   - Confirme as credenciais do Coralogix
   - Verifique se o endpoint OTLP está correto
   - Teste com `enable_console_exporter=True` para desenvolvimento

3. **Instrumentações específicas não funcionam**
   - Verifique variáveis `OTEL_PYTHON_*_INSTRUMENT`
   - Confirme se as dependências estão instaladas
   - Verifique logs para erros de instrumentação

## 📈 Métricas e Atributos

### Atributos Coralogix

- `cx.application.name`: Nome da aplicação no Coralogix
- `cx.subsystem.name`: Nome do subsistema no Coralogix
- `service.name`: Nome do serviço OpenTelemetry
- `deployment.environment`: Ambiente de deploy (dev, staging, prod)

### Atributos HTTP

- `http.method`: Método HTTP (GET, POST, etc.)
- `http.status_code`: Código de status da resposta
- `http.url`: URL completa da requisição
- `http.duration`: Duração da requisição em segundos
- `http.response_size`: Tamanho da resposta em bytes

### Atributos Django

- `django.view_name`: Nome da view Django
- `django.url_name`: Nome da URL pattern
- `django.app_name`: Nome da aplicação Django
- `django.user`: Usuário autenticado
- `django.session`: Status da sessão

### Métricas Automáticas

- **Duração de requests**: Tempo de processamento de requisições
- **Status codes**: Distribuição de códigos HTTP
- **Tamanho de respostas**: Métricas de payload
- **Exceções**: Contagem e tipos de erros
- **Performance de queries**: Timing de operações de banco

## 🐳 Scripts de Inicialização

O pacote inclui scripts para facilitar a execução de aplicações Django com auto-instrumentação OpenTelemetry:

- **`entrypoint.sh`**: Script bash para execução com auto-instrumentação
- **`gunicorn.config.py`**: Configuração otimizada do Gunicorn para OpenTelemetry
- **Uso Automático**: Referência automática ao gunicorn.config.py da biblioteca quando não há arquivo local

### Script de Entrypoint (`entrypoint.sh`)

#### Uso Básico

```bash
# Executar com Gunicorn (produção)
./entrypoint.sh gunicorn

# Executar com Django Development Server
./entrypoint.sh runserver

# Executar setup (migrations, collectstatic)
./entrypoint.sh setup

# Executar comandos Django
./entrypoint.sh manage.py migrate
./entrypoint.sh manage.py shell
```

#### Características do Entrypoint

- **Estratégia Híbrida**: Combina auto-instrumentação com configuração manual
- **Setup Automático**: Executa migrations e collectstatic automaticamente
- **Suporte a Múltiplos Servidores**: Gunicorn, Django runserver, Uvicorn
- **Ambientes Flexíveis**: Desenvolvimento local e produção
- **Compatibilidade**: Docker, Kubernetes, desenvolvimento local

### Configuração do Gunicorn (`gunicorn.config.py`)

#### Uso Automático com Entrypoint

```bash
# Uso simplificado - usa automaticamente o config da biblioteca
./entrypoint.sh gunicorn

# Com variáveis de ambiente personalizadas
export GUNICORN_WORKERS=8
export GUNICORN_THREADS=4
./entrypoint.sh gunicorn
```

#### Uso com Configuração Local

```bash
# Se você tiver um gunicorn.config.py local, ele terá prioridade
./entrypoint.sh gunicorn

# Ou especificar explicitamente
export GUNICORN_CONFIG="--config gunicorn.config.py myproject.wsgi:application"
./entrypoint.sh gunicorn
```

#### Uso Direto

```bash
# Executar Gunicorn com configuração da biblioteca
opentelemetry-instrument gunicorn --config gunicorn.config.py myproject.wsgi:application
```

#### Características da Configuração

- **Uso Automático**: O entrypoint.sh referencia automaticamente o arquivo da biblioteca
- **Otimizado para OpenTelemetry**: Configurações específicas para auto-instrumentação
- **Performance**: Workers e threads otimizados para diferentes ambientes
- **Logging**: Logs estruturados compatíveis com OpenTelemetry
- **Hooks**: Hooks para monitoramento e debugging
- **Compatibilidade**: Suporte a WSGI e ASGI
- **Zero Configuração**: Não é necessário copiar o arquivo para o projeto

#### Variáveis de Ambiente para Gunicorn

```bash
# Configurações básicas
GUNICORN_BIND=0.0.0.0:8000
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
GUNICORN_WORKER_CLASS=sync

# Configurações de performance
GUNICORN_TIMEOUT=30
GUNICORN_KEEPALIVE=5
GUNICORN_MAX_REQUESTS=1000
GUNICORN_MAX_REQUESTS_JITTER=100

# Configurações de logging
GUNICORN_LOG_LEVEL=info
GUNICORN_ACCESS_LOG=-
GUNICORN_ERROR_LOG=-

# Configurações específicas para ASGI
GUNICORN_WORKER_CLASS=uvicorn.workers.UvicornWorker
GUNICORN_ASGI_OPTIMIZED=true
```

## 🚀 Configuração Automática do Gunicorn

A biblioteca `django-coralogix-otel` agora fornece configuração automática do Gunicorn, eliminando a necessidade de copiar arquivos de configuração para seus projetos.

### Como Funciona

1. **Detecção Automática**: Ao executar `./entrypoint.sh gunicorn`, o script verifica se existe um arquivo `gunicorn.config.py` no diretório do projeto
2. **Uso da Biblioteca**: Se não encontrar um arquivo local, o script automaticamente utiliza o `gunicorn.config.py` fornecido pela biblioteca
3. **Prioridade Local**: Arquivos de configuração locais sempre têm prioridade sobre o da biblioteca
4. **Configuração Otimizada**: O arquivo da biblioteca é pré-otimizado para OpenTelemetry e performance

### Benefícios

- **Zero Configuração**: Não há necessidade de copiar ou manter arquivos de configuração
- **Sempre Atualizado**: A configuração é mantida e atualizada junto com a biblioteca
- **Otimização Pronta**: Configuração específica para OpenTelemetry e performance
- **Flexibilidade**: Ainda permite personalização quando necessário

### Exemplos de Uso

```bash
# Uso mais simples possível - tudo configurado automaticamente
docker run -e CORALOGIX_PRIVATE_KEY=... my-django-image

# Ou localmente
./entrypoint.sh gunicorn
```

### Documentação Completa

Para documentação detalhada sobre os scripts de inicialização, consulte:
- [ENTRYPOINT.md](ENTRYPOINT.md) - Documentação do script de entrypoint
- [EXAMPLES.md](EXAMPLES.md) - Exemplos de uso e integração

## 🐳 Integração com Docker

### Dockerfile Exemplo com Entrypoint e Gunicorn Config

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Copiar scripts de inicialização
COPY entrypoint.sh /usr/local/bin/
COPY gunicorn.config.py /app/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Variáveis de ambiente para produção
ENV DJANGO_CORALOGIX_AUTO_INIT=true
ENV OTEL_LOG_LEVEL=INFO
ENV DJANGO_DEBUG=False
ENV GUNICORN_CONFIG="--config gunicorn.config.py myproject.wsgi:application"

# Expor porta
EXPOSE 8000

# Usar entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn"]
```

### Dockerfile com Configuração Avançada do Gunicorn

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Copiar configuração do Gunicorn
COPY gunicorn.config.py /app/

# Variáveis de ambiente para produção otimizada
ENV DJANGO_CORALOGIX_AUTO_INIT=true
ENV OTEL_LOG_LEVEL=INFO
ENV DJANGO_DEBUG=False
ENV GUNICORN_WORKERS=8
ENV GUNICORN_THREADS=4
ENV GUNICORN_MAX_REQUESTS=2000
ENV GUNICORN_TIMEOUT=60

# Expor porta
EXPOSE 8000

# Comando de inicialização com auto-instrumentação
CMD ["opentelemetry-instrument", "gunicorn", "--config", "gunicorn.config.py", "myproject.wsgi:application"]
```

### Dockerfile Tradicional (sem entrypoint)

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

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Docker Compose para Desenvolvimento

```yaml
version: '3.8'
services:
  django-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CORALOGIX_PRIVATE_KEY=${CORALOGIX_PRIVATE_KEY}
      - OTEL_EXPORTER_OTLP_ENDPOINT=https://ingress.coralogix.com:443
      - OTEL_SERVICE_NAME=myapp-dev
      - OTEL_LOG_LEVEL=DEBUG
      - DJANGO_DEBUG=True
      - DJANGO_CORALOGIX_AUTO_INIT=true
    volumes:
      - .:/app
```

## 🤝 Contribuindo

### Desenvolvimento Local

1. **Fork o repositório**
2. **Clone seu fork**
   ```bash
   git clone https://github.com/your-username/django-coralogix-otel.git
   cd django-coralogix-otel
   ```

3. **Configurar ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   ```

4. **Instalar dependências de desenvolvimento**
   ```bash
   pip install -e ".[dev]"
   ```

5. **Executar testes**
   ```bash
   pytest
   ```

6. **Verificar qualidade de código**
   ```bash
   black django_coralogix_otel tests
   flake8 django_coralogix_otel tests
   mypy django_coralogix_otel
   ```

### Processo de Contribuição

1. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
2. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
3. Push para a branch (`git push origin feature/AmazingFeature`)
4. Abra um Pull Request

### Diretrizes de Código

- Siga as convenções PEP 8
- Use type hints sempre que possível
- Escreva testes para novas funcionalidades
- Mantenha a compatibilidade com versões anteriores
- Documente novas funcionalidades no README

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## 🆘 Suporte

### Recursos

- [Documentação OpenTelemetry](https://opentelemetry.io/docs/)
- [Documentação Coralogix](https://coralogix.com/docs/)
- [Documentação Django](https://docs.djangoproject.com/)

### Comunidade

- [Issues do Projeto](https://github.com/vertc-developers/django-coralogix-otel/issues)
- [Discussions](https://github.com/vertc-developers/django-coralogix-otel/discussions)
- [Pull Requests](https://github.com/vertc-developers/django-coralogix-otel/pulls)

### Troubleshooting Avançado

#### Verificar Exportação de Dados

```python
from opentelemetry import trace
from django_coralogix_otel import get_otel_config

# Verificar configuração atual
config = get_otel_config()
print(f"Configuração: {config}")

# Verificar se o tracer está funcionando
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("test_span") as span:
    span.set_attribute("test.attribute", "value")
    print("✅ Span criado com sucesso")
```

#### Monitorar Performance

```python
import time
from django_coralogix_otel import get_tracer

def monitor_performance():
    tracer = get_tracer("performance.monitor")

    with tracer.start_as_current_span("performance_test") as span:
        start_time = time.time()

        # Operação a ser monitorada
        time.sleep(0.1)

        duration = time.time() - start_time
        span.set_attribute("performance.duration", duration)

        if duration > 0.5:
            span.set_attribute("performance.slow", True)
```

## 🔄 Changelog

### v0.1.0 (2024-XX-XX)
- **Funcionalidades**:
  - Implementação inicial da estratégia híbrida
  - Suporte completo às variáveis de ambiente do Kubernetes
  - Middleware Django com atributos Coralogix
  - Instrumentações para Django, PostgreSQL, Requests, Logging
  - Exportadores OTLP e Console
  - Fallbacks robustos para operação sem OpenTelemetry

- **Melhorias**:
  - Configuração automática baseada em variáveis de ambiente
  - Validação robusta de configuração
  - Logging estruturado com OpenTelemetry
  - Suporte a WSGI e ASGI
  - Integração com Docker e Kubernetes

## 📞 Contato

- **Email**: thiagosistemas3@gmail.com
- **GitHub**: [vertc-developers/django-coralogix-otel](https://github.com/vertc-developers/django-coralogix-otel)
- **Issues**: [Reportar Problema](https://github.com/vertc-developers/django-coralogix-otel/issues)

## 🙏 Agradecimentos

- [OpenTelemetry Python](https://github.com/open-telemetry/opentelemetry-python) - Por fornecer a base de instrumentação
- [Coralogix](https://coralogix.com/) - Por fornecer a plataforma de observabilidade
- [Django](https://www.djangoproject.com/) - Por ser um framework web fantástico

---

**django-coralogix-otel** - Auto-instrumentação OpenTelemetry com Coralogix para aplicações Django 🚀