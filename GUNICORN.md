# Configuração do Gunicorn para django-coralogix-otel

## 📋 Visão Geral

O arquivo `gunicorn.config.py` fornece uma configuração otimizada do Gunicorn para uso com o pacote `django-coralogix-otel`. Ele inclui configurações específicas para OpenTelemetry, hooks de monitoramento e otimizações de performance para diferentes ambientes.

## 🚀 Uso Básico

### Uso Automático com Entrypoint (Recomendado)

```bash
# Uso mais simples - usa automaticamente o config da biblioteca
./entrypoint.sh gunicorn

# Com variáveis de ambiente personalizadas
export GUNICORN_WORKERS=8
export GUNICORN_THREADS=4
./entrypoint.sh gunicorn
```

### Com Entrypoint Script (Configuração Local)

```bash
# Se você tiver um gunicorn.config.py local, ele terá prioridade
./entrypoint.sh gunicorn

# Ou especificar explicitamente
export GUNICORN_CONFIG="--config gunicorn.config.py myproject.wsgi:application"
./entrypoint.sh gunicorn
```

### Uso Direto

```bash
# Executar Gunicorn com configuração da biblioteca
opentelemetry-instrument gunicorn --config gunicorn.config.py myproject.wsgi:application
```

## 📦 Uso Automático da Biblioteca

O `django-coralogix-otel` agora fornece configuração automática do Gunicorn, eliminando a necessidade de copiar arquivos para seus projetos.

### Como Funciona

1. **Detecção Automática**: O entrypoint.sh verifica se existe um arquivo `gunicorn.config.py` no diretório do projeto
2. **Uso da Biblioteca**: Se não encontrar um arquivo local, ele automaticamente utiliza o arquivo da biblioteca
3. **Prioridade Local**: Arquivos locais sempre têm prioridade sobre o da biblioteca
4. **Zero Configuração**: Não é necessário copiar ou manter arquivos de configuração

### Vantagens

- **Simplicidade**: Não há necessidade de copiar arquivos de configuração
- **Manutenção**: A configuração é mantida e atualizada com a biblioteca
- **Otimizada**: Configuração específica para OpenTelemetry
- **Flexibilidade**: Ainda permite configurações locais quando necessário

### Com Docker

```dockerfile
# Dockerfile com uso automático (recomendado)
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Copiar script de entrypoint
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Variáveis de ambiente
ENV DJANGO_CORALOGIX_AUTO_INIT=true
ENV GUNICORN_WORKERS=4
ENV GUNICORN_THREADS=2

# Usar entrypoint (usará automaticamente o config da biblioteca)
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn"]
```

### Docker com Configuração Local

```dockerfile
# Dockerfile tradicional com configuração local
FROM python:3.9-slim

WORKDIR /app

# Copiar configuração do Gunicorn
COPY gunicorn.config.py /app/

# Variáveis de ambiente
ENV GUNICORN_WORKERS=4
ENV GUNICORN_THREADS=2

# Comando de inicialização
CMD ["opentelemetry-instrument", "gunicorn", "--config", "gunicorn.config.py", "myproject.wsgi:application"]
```

## ⚙️ Configurações Disponíveis

### Configurações Básicas

| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `GUNICORN_BIND` | Endereço e porta para bind | `0.0.0.0:8000` |
| `GUNICORN_WORKERS` | Número de workers | `cpu_count * 2 + 1` |
| `GUNICORN_THREADS` | Número de threads por worker | `2` |
| `GUNICORN_WORKER_CLASS` | Classe do worker | `sync` |

### Configurações de Performance

| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `GUNICORN_TIMEOUT` | Timeout de requisição (segundos) | `30` |
| `GUNICORN_KEEPALIVE` | Keepalive (segundos) | `5` |
| `GUNICORN_MAX_REQUESTS` | Máximo de requisições por worker | `1000` |
| `GUNICORN_MAX_REQUESTS_JITTER` | Jitter para max_requests | `100` |
| `GUNICORN_PRELOAD_APP` | Pré-carregar aplicação | `false` |

### Configurações de Logging

| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `GUNICORN_LOG_LEVEL` | Nível de log | `info` |
| `GUNICORN_ACCESS_LOG` | Arquivo de log de acesso | `-` (stdout) |
| `GUNICORN_ERROR_LOG` | Arquivo de log de erro | `-` (stdout) |

### Configurações de Segurança

| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `GUNICORN_LIMIT_REQUEST_LINE` | Tamanho máximo da linha de requisição | `4094` |
| `GUNICORN_LIMIT_REQUEST_FIELDS` | Número máximo de campos | `100` |
| `GUNICORN_LIMIT_REQUEST_FIELD_SIZE` | Tamanho máximo do campo | `8190` |

### Configurações para ASGI

| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `GUNICORN_WORKER_CLASS` | Classe para ASGI | `uvicorn.workers.UvicornWorker` |
| `GUNICORN_ASGI_OPTIMIZED` | Otimizações para ASGI | `false` |
| `GUNICORN_WORKER_CONNECTIONS` | Conexões por worker (ASGI) | `1000` |

## 🔧 Hooks e Callbacks

### `when_ready(server)`
Executado quando o Gunicorn está pronto para aceitar conexões.

```python
def when_ready(server):
    server.log.info("Gunicorn ready to accept connections")
    server.log.info(f"Bind: {bind}")
    server.log.info(f"Workers: {workers}")
```

### `post_fork(server, worker)`
Executado após o fork do worker.

```python
def post_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")
    if os.environ.get("OTEL_PYTHON_INSTRUMENTATION_ENABLED"):
        server.log.info("✅ OpenTelemetry auto-instrumentation active")
```

### `pre_request(worker, req)`
Executado antes de processar cada requisição.

```python
def pre_request(worker, req):
    worker.log.debug(f"Starting request: {req.method} {req.path}")
```

### `post_request(worker, req, environ, resp)`
Executado após processar cada requisição.

```python
def post_request(worker, req, environ, resp):
    worker.log.debug(f"Completed request: {req.method} {req.path} -> {resp.status}")
```

## 🎯 Configurações Recomendadas

### Desenvolvimento Local

```bash
# Configurações para desenvolvimento
export GUNICORN_WORKERS=2
export GUNICORN_THREADS=1
export GUNICORN_TIMEOUT=60
export GUNICORN_LOG_LEVEL=debug
export GUNICORN_PRELOAD_APP=false
```

### Produção (WSGI)

```bash
# Configurações otimizadas para produção WSGI
export GUNICORN_WORKERS=8
export GUNICORN_THREADS=4
export GUNICORN_TIMEOUT=30
export GUNICORN_MAX_REQUESTS=2000
export GUNICORN_PRELOAD_APP=true
export GUNICORN_LOG_LEVEL=info
```

### Produção (ASGI)

```bash
# Configurações otimizadas para produção ASGI
export GUNICORN_WORKER_CLASS=uvicorn.workers.UvicornWorker
export GUNICORN_WORKERS=4
export GUNICORN_ASGI_OPTIMIZED=true
export GUNICORN_WORKER_CONNECTIONS=1000
export GUNICORN_PRELOAD_APP=true
```

### Kubernetes

```bash
# Configurações para Kubernetes
export GUNICORN_WORKERS=4
export GUNICORN_THREADS=2
export GUNICORN_MAX_REQUESTS=1000
export GUNICORN_TIMEOUT=30
export GUNICORN_PRELOAD_APP=true
```

## 🔍 Troubleshooting

### Verificar Configuração

```bash
# Testar configuração do Gunicorn
gunicorn --check-config gunicorn.config.py myproject.wsgi:application

# Verificar variáveis de ambiente
env | grep GUNICORN
```

### Logs de Depuração

```bash
# Habilitar logs detalhados
export GUNICORN_LOG_LEVEL=debug

# Executar com logs detalhados
opentelemetry-instrument gunicorn --config gunicorn.config.py myproject.wsgi:application
```

### Problemas Comuns

1. **Workers não iniciam**
   - Verifique se `GUNICORN_PRELOAD_APP` está configurado corretamente
   - Confirme que a aplicação Django está funcionando
   - Verifique logs de erro do Gunicorn

2. **Timeout de requisições**
   - Aumente `GUNICORN_TIMEOUT` para operações longas
   - Verifique se há deadlocks na aplicação
   - Monitore uso de CPU e memória

3. **Problemas de memória**
   - Reduza `GUNICORN_WORKERS` se necessário
   - Ajuste `GUNICORN_MAX_REQUESTS` para reiniciar workers periodicamente
   - Monitore uso de memória com ferramentas como `psutil`

## 📊 Monitoramento

### Métricas do Gunicorn

O Gunicorn expõe métricas que podem ser coletadas pelo OpenTelemetry:

- **Workers ativos**: Número de workers em execução
- **Requisições processadas**: Contador de requisições
- **Tempo de resposta**: Métricas de performance
- **Erros**: Contador de erros por tipo

### Integração com OpenTelemetry

```python
# Exemplo de métricas customizadas
from opentelemetry import metrics

meter = metrics.get_meter("gunicorn.metrics")
requests_counter = meter.create_counter("gunicorn.requests")

def post_request(worker, req, environ, resp):
    requests_counter.add(1, {"method": req.method, "status": resp.status})
```

## 🔄 Compatibilidade

### Versões do Python
- Python 3.7+
- Compatível com virtualenv e pip

### Versões do Gunicorn
- Gunicorn 20.0+
- Suporte a workers sync e async

### Integrações
- **OpenTelemetry**: Compatível com auto-instrumentação
- **Django**: WSGI e ASGI
- **Docker**: Configurações otimizadas para containers
- **Kubernetes**: Variáveis de ambiente para pods

## 🔗 Links Relacionados

- [django-coralogix-otel README](README.md)
- [ENTRYPOINT.md](ENTRYPOINT.md) - Documentação do script de entrypoint
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)