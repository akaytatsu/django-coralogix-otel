# Script de Entrypoint para django-coralogix-otel

## 📋 Visão Geral

O script `entrypoint.sh` fornece uma interface de linha de comando para executar aplicações Django com auto-instrumentação OpenTelemetry usando o pacote `django-coralogix-otel`. Ele implementa a estratégia híbrida (auto-instrumentação + configuração manual) e é compatível com Docker, Kubernetes e diferentes ambientes.

## 🚀 Uso Básico

### Executar com Gunicorn (Produção)
```bash
./entrypoint.sh gunicorn
```

### Executar com Django Development Server
```bash
./entrypoint.sh runserver
```

### Executar com Uvicorn (ASGI)
```bash
./entrypoint.sh uvicorn
```

### Executar Setup do Django
```bash
./entrypoint.sh setup
```

### Executar Comandos Django
```bash
./entrypoint.sh manage.py migrate
./entrypoint.sh manage.py createsuperuser
./entrypoint.sh manage.py shell
```

### Executar Scripts Python
```bash
./entrypoint.sh python my_script.py
```

## ⚙️ Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `gunicorn` | Inicia servidor Gunicorn com setup automático |
| `runserver` | Inicia servidor de desenvolvimento Django |
| `uvicorn` | Inicia servidor Uvicorn para aplicações ASGI |
| `setup` | Executa apenas setup (migrations, collectstatic) |
| `manage.py [args]` | Executa comandos de gerenciamento Django |
| `python [script] [args]` | Executa scripts Python com instrumentação |
| `custom [command] [args]` | Executa comandos customizados |

## 🔧 Variáveis de Ambiente

### Configuração Básica
```bash
# Obrigatórias
CORALOGIX_PRIVATE_KEY=your-private-key
OTEL_EXPORTER_OTLP_ENDPOINT=https://ingress.coralogix.com:443

# Opcionais com valores padrão
OTEL_SERVICE_NAME=django-app
CORALOGIX_APPLICATION_NAME=my-application
CORALOGIX_SUBSYSTEM_NAME=backend
OTEL_DEPLOYMENT_ENVIRONMENT=production
```

### Configuração de Setup
```bash
# Pular setup automático
SKIP_DJANGO_SETUP=true

# Comandos extras de setup
DJANGO_EXTRA_SETUP_COMMANDS=createcachetable,collectstatic
```

### Configuração de Servidores
```bash
# Configuração customizada do Gunicorn
GUNICORN_CONFIG="--bind 0.0.0.0:8000 --workers 8 --threads 4"

# Configuração customizada do Uvicorn
UVICORN_CONFIG="--host 0.0.0.0 --port 8000 --workers 8"
```

### Ambiente de Desenvolvimento
```bash
# Habilitar console exporters
APP_ENVIRONMENT=local
DJANGO_DEBUG=True
OTEL_LOG_LEVEL=DEBUG
```

## 🐳 Integração com Docker

### Dockerfile Exemplo
```dockerfile
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
ENV OTEL_LOG_LEVEL=INFO
ENV DJANGO_DEBUG=False

# Expor porta
EXPOSE 8000

# Usar entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn"]
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
      - APP_ENVIRONMENT=local
    volumes:
      - .:/app
    command: ["runserver"]
```

## ☸️ Integração com Kubernetes

### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: django-opentelemetry
data:
  OTEL_SERVICE_NAME: "my-django-app"
  OTEL_EXPORTER_OTLP_ENDPOINT: "https://ingress.coralogix.com:443"
  OTEL_DEPLOYMENT_ENVIRONMENT: "production"
  CORALOGIX_APPLICATION_NAME: "my-application"
  CORALOGIX_SUBSYSTEM_NAME: "backend"
  SKIP_DJANGO_SETUP: "false"
```

### Deployment
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
        command: ["/usr/local/bin/entrypoint.sh"]
        args: ["gunicorn"]
        envFrom:
        - configMapRef:
            name: django-opentelemetry
        - secretRef:
            name: coralogix-secret
        env:
        - name: GUNICORN_CONFIG
          value: "--bind 0.0.0.0:8000 --workers 4 --threads 2"
```

## 🔄 Estratégia Híbrida

O script implementa a estratégia híbrida do `django-coralogix-otel`:

1. **Auto-instrumentação**: Usa `opentelemetry-instrument` para wrap automático
2. **Configuração Manual**: Configura variáveis de ambiente para instrumentações específicas
3. **Fallback Robusto**: Continua funcionando mesmo sem OpenTelemetry disponível

### Variáveis de Instrumentação Habilitadas
```bash
OTEL_PYTHON_DJANGO_INSTRUMENT=true
OTEL_PYTHON_REQUESTS_INSTRUMENT=true
OTEL_PYTHON_PSYCOPG2_INSTRUMENT=true
OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
OTEL_PYTHON_WSGI_INSTRUMENT=true
OTEL_PYTHON_ASGI_INSTRUMENT=true
```

## 📦 Uso Automático do gunicorn.config.py da Biblioteca

O script `entrypoint.sh` agora possui suporte automático para o arquivo de configuração do Gunicorn fornecido pela biblioteca `django-coralogix-otel`, simplificando ainda mais a configuração para produção.

### Funcionalidade

- **Detecção Automática**: O entrypoint.sh procura automaticamente pelo arquivo `gunicorn.config.py` na biblioteca instalada
- **Configuração Otimizada**: Utiliza uma configuração pré-otimizada para OpenTelemetry e performance
- **Prioridade Local**: Se um arquivo `gunicorn.config.py` local for encontrado no projeto, ele terá prioridade sobre o da biblioteca
- **Zero Configuração**: Não é necessário copiar ou manter arquivos de configuração no projeto

### Como Funciona

1. Ao executar `./entrypoint.sh gunicorn`, o script verifica se existe um arquivo `gunicorn.config.py` no diretório atual
2. Se não encontrar um arquivo local, ele automaticamente referencia o arquivo da biblioteca `django-coralogix-otel`
3. A configuração da biblioteca é otimizada para OpenTelemetry, com workers, threads e logging apropriados

### Exemplo de Uso

```bash
# Uso simples - usa automaticamente o config da biblioteca
./entrypoint.sh gunicorn

# Com variáveis de ambiente personalizadas
export GUNICORN_WORKERS=8
export GUNICORN_THREADS=4
./entrypoint.sh gunicorn

# Com configuração customizada (sobrescreve o da biblioteca)
./entrypoint.sh gunicorn --bind 0.0.0.0:9000 --workers 12
```

### Vantagens

- **Simplicidade**: Não há necessidade de copiar arquivos de configuração para cada projeto
- **Manutenção**: A configuração é mantida e atualizada junto com a biblioteca
- **Otimizada**: Configuração específica para OpenTelemetry e performance
- **Flexibilidade**: Ainda permite configurações locais quando necessário

### Compatibilidade

Esta funcionalidade é compatível com:
- Docker containers
- Kubernetes deployments
- Ambientes de desenvolvimento local
- Servidores de produção

## 🛠️ Exemplos de Uso

### Desenvolvimento Local
```bash
# Configurar ambiente
export CORALOGIX_PRIVATE_KEY=dev-key
export OTEL_EXPORTER_OTLP_ENDPOINT=https://ingress.coralogix.com:443
export OTEL_SERVICE_NAME=myapp-dev
export OTEL_LOG_LEVEL=DEBUG
export DJANGO_DEBUG=True
export APP_ENVIRONMENT=local

# Executar servidor de desenvolvimento
./entrypoint.sh runserver
```

### Produção com Gunicorn
```bash
# Configurar ambiente de produção
export CORALOGIX_PRIVATE_KEY=prod-key
export OTEL_EXPORTER_OTLP_ENDPOINT=https://ingress.coralogix.com:443
export OTEL_SERVICE_NAME=myapp-prod
export OTEL_DEPLOYMENT_ENVIRONMENT=production
export GUNICORN_CONFIG="--bind 0.0.0.0:8000 --workers 8 --threads 4"

# Executar Gunicorn
./entrypoint.sh gunicorn
```

### Setup e Migrations
```bash
# Executar apenas setup
./entrypoint.sh setup

# Executar migrations específicas
./entrypoint.sh manage.py migrate myapp

# Criar superusuário
./entrypoint.sh manage.py createsuperuser --no-input
```

### Comandos Customizados
```bash
# Executar script Python customizado
./entrypoint.sh custom python my_custom_script.py

# Executar comando shell
./entrypoint.sh custom bash -c "echo 'Hello World'"
```

## 🔍 Troubleshooting

### Verificar se o Script Está Funcionando
```bash
# Testar help
./entrypoint.sh

# Verificar permissões
ls -la entrypoint.sh

# Testar comando simples
./entrypoint.sh manage.py check
```

### Logs de Depuração
```bash
# Habilitar logs detalhados
export OTEL_LOG_LEVEL=DEBUG
export DJANGO_DEBUG=True

# Executar com logs
./entrypoint.sh runserver
```

### Problemas Comuns

1. **Permissões do Script**
   ```bash
   chmod +x entrypoint.sh
   ```

2. **Variáveis de Ambiente Não Definidas**
   - Verifique se `CORALOGIX_PRIVATE_KEY` está definida
   - Confirme que `OTEL_EXPORTER_OTLP_ENDPOINT` é válido

3. **Setup Falhando**
   - Use `SKIP_DJANGO_SETUP=true` para pular setup
   - Verifique se o banco de dados está acessível

## 📋 Compatibilidade

- **Python**: 3.7+
- **Django**: 3.2+
- **OpenTelemetry**: 1.20+
- **Servidores**: Gunicorn, Django runserver, Uvicorn
- **Ambientes**: Docker, Kubernetes, Desenvolvimento Local

## 🔗 Links Relacionados

- [django-coralogix-otel README](README.md)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Coralogix Documentation](https://coralogix.com/docs/)