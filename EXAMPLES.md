
# Exemplos de Uso - django-coralogix-otel

Este arquivo contém exemplos detalhados de uso do pacote `django-coralogix-otel` em diferentes cenários.

## 📋 Índice

1. [Configuração Básica](#configuração-básica)
2. [Integração com Django](#integração-com-django)
3. [Uso em Views](#uso-em-views)
4. [Configuração Kubernetes](#configuração-kubernetes)
5. [Desenvolvimento Local](#desenvolvimento-local)
6. [Scripts de Inicialização](#scripts-de-inicialização)
7. [Testes e Validação](#testes-e-validação)
8. [Troubleshooting](#troubleshooting)

## 🔧 Configuração Básica

### Exemplo 1: Configuração Mínima

```python
# settings.py
import os
from django_coralogix_otel import configure_django_settings

# Configurar variáveis de ambiente
os.environ.update({
    "CORALOGIX_PRIVATE_KEY": "your-private-key",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "https://ingress.coralogix.com:443",
    "OTEL_SERVICE_NAME": "my-django-app",
    "DJANGO_CORALOGIX_AUTO_INIT": "true",
})

# Configurar Django
otel_settings = configure_django_settings()
MIDDLEWARE = otel_settings['MIDDLEWARE'] + MIDDLEWARE

if 'LOGGING' in otel_settings:
    LOGGING = otel_settings['LOGGING']
```

### Exemplo 2: Configuração Completa

```python
# settings.py
import os
from django_coralogix_otel import configure_django_settings

# Variáveis de ambiente completas
os.environ.update({
    # Obrigatórias
    "CORALOGIX_PRIVATE_KEY": "your-private-key",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "https://ingress.coralogix.com:443",
    
    # Identificação
    "OTEL_SERVICE_NAME": "my-django-app",
    "CORALOGIX_APPLICATION_NAME": "my-application",
    "CORALOGIX_SUBSYSTEM_NAME": "backend",
    "OTEL_SERVICE_NAMESPACE": "production",
    "OTEL_SERVICE_VERSION": "1.0.0",
    
    # Ambiente
    "OTEL_DEPLOYMENT_ENVIRONMENT": "production",
    
    # Instrumentações
    "OTEL_PYTHON_DJANGO_INSTRUMENT": "true",
    "OTEL_PYTHON_REQUESTS_INSTRUMENT": "true",
    "OTEL_PYTHON_PSYCOPG2_INSTRUMENT": "true",
    "OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED": "true",
    "OTEL_PYTHON_KAFKA_INSTRUMENT": "false",
    
    # Configuração
    "DJANGO_CORALOGIX_AUTO_INIT": "true",
    "OTEL_LOG_LEVEL": "INFO",
})

# Configurar Django
otel_settings = configure_django_settings()
MIDDLEWARE = otel_settings['MIDDLEWARE'] + MIDDLEWARE

if 'LOGGING' in otel_settings:
    LOGGING = otel_settings['LOGGING']
```

## 🚀 Integração com Django

### Exemplo 3: wsgi.py

```python
# wsgi.py
import os
from django_coralogix_otel import initialize_opentelemetry

# Inicializar OpenTelemetry antes do Django
print("🔄 Inicializando OpenTelemetry...")
if initialize_opentelemetry():
    print("✅ OpenTelemetry inicializado com sucesso")
else:
    print("⚠️  OpenTelemetry não pôde ser inicializado")

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Exemplo 4: asgi.py

```python
# asgi.py
import os
from django_coralogix_otel import initialize_opentelemetry

# Inicializar OpenTelemetry
initialize_opentelemetry()

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
from django.core.asgi import get_asgi_application
application = get_asgi_application()
```

### Exemplo 5: Configuração com Gunicorn

```python
# gunicorn.conf.py
import os
from django_coralogix_otel import initialize_opentelemetry

# Inicializar OpenTelemetry antes dos workers
def on_starting(server):
    print("🚀 Inicializando OpenTelemetry para Gunicorn...")
    if initialize_opentelemetry():
        print("✅ OpenTelemetry configurado")
    else:
        print("⚠️  OpenTelemetry não disponível")

# Configurações do Gunicorn
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
```

## 🎯 Uso em Views

### Exemplo 6: View Básica com Tracing

```python
# views.py
from django.http import JsonResponse
from django.views import View
from django_coralogix_otel import get_tracer

class UserListView(View):
    def get(self, request):
        tracer = get_tracer("users.views")
        
        with tracer.start_as_current_span("list_users") as span:
            # Adicionar atributos do usuário
            span.set_attribute("user.id", request.user.id if request.user.is_authenticated else "anonymous")
            span.set_attribute("http.method", request.method)
            
            # Simular processamento
            users = self._get_users()
            
            # Adicionar métricas
            span.set_attribute("users.count", len(users))
            span.set_attribute("operation.success", True)
            
            return JsonResponse({"users": users})
    
    def _get_users(self):
        # Simular acesso ao banco
        import time
        time.sleep(0.1)
        return [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
```

### Exemplo 7: View com Tratamento de Erros

```python
# views.py
from django.http import JsonResponse
from django.views import View
from django_coralogix_otel import get_tracer

class DataProcessView(View):
    def post(self, request):
        tracer = get_tracer("data.views")
        
        with tracer.start_as_current_span("process_data") as span:
            try:
                span.set_attribute("user.id", request.user.id)
                span.set_attribute("data.size", len(request.body))
                
                # Processar dados
                result = self._process_data(request.body)
                
                span.set_attribute("result.size", len(result))
                span.set_attribute("operation.success", True)
                
                return JsonResponse({"status": "success", "data": result})
                
            except Exception as e:
                # Registrar erro no span
                span.record_exception(e)
                span.set_attribute("operation.success", False)
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
                
                return JsonResponse(
                    {"status": "error", "message": str(e)}, 
                    status=500
                )
    
    def _process_data(self, data):
        # Simular processamento complexo
        import json
        import time
        
        data_dict = json.loads(data)
        time.sleep(0.2)  # Simular processamento
        
        return {"processed": True, "items": len(data_dict)}
```

### Exemplo 8: View com Métricas Customizadas

```python
# views.py
from django.http import JsonResponse
from django.views import View
from django_coralogix_otel import get_tracer, get_meter

class MetricsView(View):
    def __init__(self):
        super().__init__()
        self.meter = get_meter("custom.metrics")
        self.request_counter = self.meter.create_counter(
            "http_requests_total",
            description="Total de requisições HTTP"
        )
    
    def get(self, request):
        tracer = get_tracer("metrics.views")
        
        with tracer.start_as_current_span("metrics_endpoint") as span:
            # Registrar métrica
            self.request_counter.add(1, {
                "method": request.method,
                "endpoint": "metrics",
                "status": "200"
            })
            
            # Adicionar atributos
            span.set_attribute("endpoint.type", "metrics")
            span.set_attribute("response.format", "json")
            
            metrics_data = {
                "requests_total": 1000,
                "active_users": 150,
                "response_time_avg": 45.2
            }
            
            return JsonResponse(metrics_data)
```

## ☸️ Configuração Kubernetes

### Exemplo 9: ConfigMap Completo

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: django-opentelemetry
  namespace: production
data:
  # Identificação do serviço
  OTEL_SERVICE_NAME: "my-django-app"
  CORALOGIX_APPLICATION_NAME: "my-application"
  CORALOGIX_SUBSYSTEM_NAME: "backend"
  OTEL_SERVICE_NAMESPACE: "production"
  OTEL_SERVICE_VERSION: "1.0.0"
  
  # Endpoint
  OTEL_EXPORTER_OTLP_ENDPOINT: "https://ingress.coralogix.com:443"
  
  # Ambiente
  OTEL_DEPLOYMENT_ENVIRONMENT: "production"
  
  # Atributos de resource
  OTEL_RESOURCE_ATTRIBUTES: "k8s.namespace=production,k8s.pod.name=$(POD_NAME),k8s.deployment.name=myapp"
  
  # Instrumentações
  OTEL_PYTHON_DJANGO_INSTRUMENT: "true"
  OTEL_PYTHON_REQUESTS_INSTRUMENT: "true"
  OTEL_PYTHON_PSYCOPG2_INSTRUMENT: "true"
  OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED: "true"
  OTEL_PYTHON_WSGI_INSTRUMENT: "true"
  OTEL_PYTHON_ASGI_INSTRUMENT: "true"
  
  # Configuração
  DJANGO_CORALOGIX_AUTO_INIT: "true"
  OTEL_LOG_LEVEL: "INFO"
```

### Exemplo 10: Deployment com Variáveis de Ambiente

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-app
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: django-app
  template:
    metadata:
      labels:
        app: django-app
    spec:
      containers:
      - name: django-app
        image: my-registry/django-app:latest
        ports:
        - containerPort: 8000
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
        - name: KUBERNETES_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 💻 Desenvolvimento Local

### Exemplo 11: Configuração para Desenvolvimento

```python
# development.py
import os
import logging
from django_coralogix_otel import (
    initialize_opentelemetry,
    get_initialization_status,
    get_enabled_instrumentations
)

# Configurar para desenvolvimento
os.environ.update({
    "CORALOGIX_PRIVATE_KEY": "dev-key-not-used",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "https://ingress.coralogix.com:443",
    "OTEL_SERVICE_NAME": "myapp-dev",
    "CORALOGIX_APPLICATION_NAME": "myapp-development",
    "CORALOGIX_SUBSYSTEM_NAME": "backend",
    "OTEL_DEPLOYMENT_ENVIRONMENT": "development",
    "OTEL_LOG_LEVEL": "DEBUG",
    "DJANGO_DEBUG": "True",
    "DJANGO_CORALOGIX_AUTO_INIT": "true",
})

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Inicializar com console exporter
print("🔧 Configurando OpenTelemetry para desenvolvimento...")
if initialize_opentelemetry(enable_console_exporter=True):
    print("✅ OpenTelemetry configurado com sucesso")
    print(f"📊 Instrumentações: {get_enabled_instrumentations()}")
else:
    print("❌ Falha na configuração OpenTelemetry")
```

### Exemplo 12: Script de Teste

```python
# test_opentelemetry.py
#!/usr/bin/env python
"""
Script para testar a configuração do OpenTelemetry localmente
"""

import os
import logging
from django_coralogix_otel import (
    initialize_opentelemetry,
    get_initialization_status,
    get_enabled_instrumentations,
    validate_environment_variables,
    get_otel_config
)

def test_configuration():
    """Testa a configuração completa do OpenTelemetry"""
    
    print("🧪 Testando configuração OpenTelemetry...")
    
    # 1. Validar variáveis de ambiente
    print("1. Validando variáveis de ambiente...")
    if validate_environment_variables():
        print("   ✅ Variáveis de ambiente OK")
    else:
        print("   ❌ Variáveis de ambiente inválidas")
        return False
    
    # 2. Inicializar OpenTelemetry
    print("2. Inicializando OpenTelemetry...")
    if initialize_opentelemetry(enable_console_exporter=True):
        print("   ✅ OpenTelemetry inicializado")
    else:
        print("   ❌ Falha na inicialização")
        return False
    
    # 3. Verificar status
    print("3. Verificando status...")
    if get_initialization_status():
        print("   ✅ Status: Ativo")
    else:
        print("   ❌ Status: Inativo")
        return False
    
    # 4. Listar instrumentações
    print("4. Instrumentações habilitadas...")
    enabled = get_enabled_instrumentations()
    for inst in enabled:
        print(f"   ✅ {inst}")
    
    # 5. Obter configuração
    print("5. Configuração atual...")
    config = get_otel_config()
    for key, value in config.items():
        print(f"   📋 {key}: {value}")
    
    print("🎉 Teste concluído com sucesso!")
    return True

if __name__ == "__main__":
    # Configurar ambiente de teste
    os.environ.update({
        "CORALOGIX_PRIVATE_KEY": "test-key",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "https://ingress.coralogix.com:443",
        "OTEL_SERVICE_NAME": "test-app",
        "DJANGO_CORALOGIX_AUTO_INIT": "true",
    })
    
    test_configuration()
```

## 🐳 Scripts de Inicialização

### Exemplo 13: Uso do Entrypoint Script

```bash
# Executar com Gunicorn (produção) - usa automaticamente o config da biblioteca
./entrypoint.sh gunicorn

# Executar com Django Development Server
./entrypoint.sh runserver

# Executar setup (migrations, collectstatic)
./entrypoint.sh setup

# Executar comandos Django
./entrypoint.sh manage.py migrate
./entrypoint.sh manage.py shell

# Executar scripts Python
./entrypoint.sh python my_script.py
```

### Exemplo 13a: Uso Automático do Gunicorn Config

```bash
# Uso mais simples possível - tudo configurado automaticamente
./entrypoint.sh gunicorn

# Com variáveis de ambiente personalizadas
export GUNICORN_WORKERS=8
export GUNICORN_THREADS=4
export GUNICORN_TIMEOUT=60
./entrypoint.sh gunicorn

# O entrypoint.sh usará automaticamente o gunicorn.config.py da biblioteca
# Não há necessidade de copiar arquivos de configuração para o projeto
```

### Exemplo 14: Configuração do Gunicorn

```python
# gunicorn.config.py - Configuração otimizada para OpenTelemetry
import os
import multiprocessing

# Configurações básicas
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
threads = int(os.getenv("GUNICORN_THREADS", 2))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "sync")

# Configurações de performance
timeout = int(os.getenv("GUNICORN_TIMEOUT", 30))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1000))

# Hooks para OpenTelemetry
def when_ready(server):
    server.log.info("Gunicorn ready with OpenTelemetry")
    if os.environ.get("OTEL_PYTHON_INSTRUMENTATION_ENABLED"):
        server.log.info("✅ OpenTelemetry auto-instrumentation enabled")

def post_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")
```

### Exemplo 15: Docker com Scripts de Inicialização

```dockerfile
# Dockerfile com uso automático (recomendado)
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Copiar apenas o script de entrypoint
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Variáveis de ambiente
ENV DJANGO_CORALOGIX_AUTO_INIT=true
ENV OTEL_LOG_LEVEL=INFO
ENV DJANGO_DEBUG=False
ENV GUNICORN_WORKERS=4
ENV GUNICORN_THREADS=2

EXPOSE 8000

# Usar entrypoint (usará automaticamente o config da biblioteca)
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn"]
```

### Exemplo 15a: Docker com Configuração Local (Opcional)

```dockerfile
# Dockerfile tradicional com configuração local
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Copiar scripts de inicialização
COPY entrypoint.sh /usr/local/bin/
COPY gunicorn.config.py /app/  # Configuração local
RUN chmod +x /usr/local/bin/entrypoint.sh

# Variáveis de ambiente
ENV DJANGO_CORALOGIX_AUTO_INIT=true
ENV OTEL_LOG_LEVEL=INFO
ENV DJANGO_DEBUG=False
ENV GUNICORN_CONFIG="--config gunicorn.config.py myproject.wsgi:application"

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn"]
```

### Exemplo 16: Kubernetes com Scripts

```yaml
# k8s/deployment.yaml com scripts
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
        env:
        - name: GUNICORN_WORKERS
          value: "4"
        - name: GUNICORN_THREADS
          value: "2"
        - name: GUNICORN_CONFIG
          value: "--config gunicorn.config.py myproject.wsgi:application"
```

## 🧪 Testes e Validação

### Exemplo 17: Testes Unitários

```python
# tests/test_opentelemetry.py
import os
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django_coralogix_otel import (
    validate_environment_variables,
    get_enabled_instrumentations,
    is_instrumentation_enabled
)

class OpenTelemetryTests(TestCase):
    
    def setUp(self):
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_validate_environment_variables_success(self):
        """Testa validação com variáveis presentes"""
        os.environ.update({
            "CORALOGIX_PRIVATE_KEY": "test-key",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "https://test.com",
        })
        
        self.assertTrue(validate_environment_variables())
    
    def test_validate_environment_variables_missing(self):
        """Testa validação com variáveis ausentes"""
        os.environ.clear()
        
        self.assertFalse(validate_environment_variables())
    
    def test_is_instrumentation_enabled(self):
        """Testa verificação de instrumentações"""
        os.environ["OTEL_PYTHON_DJANGO_INSTRUMENT"] = "true"
        os.environ["OTEL_PYTHON_REQUESTS_INSTRUMENT"] = "false"
        
        self.assertTrue(is_instrumentation_enabled("django"))
        self.assertFalse(is_instrumentation_enabled("requests"))
    
    def test_get_enabled_instrumentations(self):
        """Testa lista de instrumentações habilitadas"""
        os.environ.update({
            "OTEL_PYTHON_DJANGO_INSTRUMENT": "true",
            "OTEL_PYTHON_REQUESTS_INSTRUMENT": "true",
            "OTEL_PYTHON_PSYCOPG2_INSTRUMENT": "false",
        })
        
        enabled = get_enabled_instrumentations()
        self.assertIn("django", enabled)
        self.assertIn("requests", enabled)
        self.assertNotIn("psycopg2", enabled)
```

### Exemplo 14: Teste de Integração

```python
# tests/test_integration.py
import os
from django.test import TestCase, Client
from django.urls import reverse
from django_coralogix_otel import get_initialization_status

class IntegrationTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        # Garantir que OpenTelemetry está inicializado
        if not get_initialization_status():
            from django_coralogix_otel import initialize_opentelemetry
            initialize_opentelemetry(enable_console_exporter=True)
    
    def test_middleware_integration(self):
        """Testa que o middleware está funcionando"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar que headers OpenTelemetry estão presentes
        # (dependendo da configuração)
    
    def test_tracing_in_views(self):
        """Testa que as views estão sendo rastreadas"""
        response = self.client.get(reverse('api:users'))
        self.assertEqual(response.status_code, 200)
        
        # Em produção, verificar se traces estão sendo enviados
        # para o Coralogix
```

## 🔧 Troubleshooting

### Exemplo 15: Diagnóstico de Problemas

```python
# diagnose.py
#!/usr/bin/env python
"""
Script de diagnóstico para problemas com OpenTelemetry
"""

import os
import logging
import sys
from django_coralogix_otel import (
    validate_environment_variables,
    get_initialization_status,
    get_enabled_instrumentations,
    get_otel_config,
    is_opentelemetry_available
)

def diagnose_problems():
    """Executa diagnóstico completo"""
    
    print("🔍 Diagnóstico do OpenTelemetry")
    print("=" * 50)
    
    problems = []
    
    # 1. Verificar disponibilidade do OpenTelemetry
    print("1. Verificando disponibilidade do OpenTelemetry...")
    if is_opentelemetry_available():
        print("   ✅ OpenTelemetry disponível")
    else:
        print("   ❌ OpenTelemetry não disponível")
        problems.append("OpenTelemetry não está instalado")
    
    # 2. Validar variáveis de ambiente
    print("2. Validando variáveis de ambiente...")
    if validate_environment_variables():
        print("   ✅ Variáveis de ambiente OK")
    else:
        print("   ❌ Variáveis de ambiente inválidas")
        problems.append("Variáveis de ambiente obrigatórias ausentes")
    
    # 3. Verificar status de inicialização
    print("3. Verificando status de inicialização...")
    if get_initialization_status():
        print("   ✅ OpenTelemetry inicializado")
    else:
        print("   ❌ OpenTelemetry não inicializado")
        problems.append("Falha na inicialização do OpenTelemetry")
    
    # 4. Listar instrumentações
    print("4. Instrumentações habilitadas...")
    enabled = get_enabled_instrumentations()
    if enabled:
        for inst in enabled:
            print(f"   ✅ {inst}")
    else:
        print("   ⚠️  Nenhuma instrumentação habilitada")
        problems.append("Nenhuma instrumentação está habilitada")
    
    # 5. Mostrar configuração
    print("5. Configuração atual...")
    config = get_otel_config()
    for key, value in config.items():
        print(f"   📋 {key}: {value}")
    
    # 6. Verificar variáveis específicas
    print("6. Verificando variáveis específicas...")
    required_vars = [
        "CORALOGIX_PRIVATE_KEY",
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "OTEL_SERVICE_NAME"
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            print(f"   ✅ {var}: {masked_value}")
        else:
            print(f"   ❌ {var}: AUSENTE")
            problems.append(f"Variável {var} não definida")
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DO DIAGNÓSTICO")
    
    if problems:
        print("❌ PROBLEMAS ENCONTRADOS:")
        for i, problem in enumerate(problems, 1):
            print(f"   {i}. {problem}")
        
        print("\n💡 SUGESTÕES:")
        if "OpenTelemetry não está instalado" in problems:
            print("   - Execute: pip install opentelemetry-sdk opentelemetry-exporter-otlp")
        
        if "Variáveis de ambiente obrigatórias ausentes" in problems:
            print("   - Defina CORALOGIX_PRIVATE_KEY e OTEL_EXPORTER_OTLP_ENDPOINT")
        
        if "Falha na inicialização do OpenTelemetry" in problems:
            print("   - Verifique logs para erros de configuração")
        
        return False
    else:
        print("✅ Tudo OK! OpenTelemetry está funcionando corretamente.")
        return True

if __name__ == "__main__":
    success = diagnose_problems()
    sys.exit(0 if success else 1)
```

### Exemplo 16: Monitoramento de Performance

```python
# performance_monitor.py
import time
import logging
from django_coralogix_otel import get_tracer

class PerformanceMonitor:
    """Monitor de performance para operações críticas"""
    
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.tracer = get_tracer("performance.monitor")
    
    def __enter__(self):
        self.start_time = time.time()
        self.span = self.tracer.start_span(self.operation_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.span.set_attribute("performance.duration", duration)
        
        if exc_type:
            self.span.record_exception(exc_val)
            self.span.set_attribute("performance.success", False)
            self.span.set_attribute("error.type", exc_type.__name__)
        else:
            self.span.set_attribute("performance.success", True)
        
        # Alertar se operação for lenta
        if duration > 1.0:  # 1 segundo
            self.span.set_attribute("performance.slow", True)
            logging.warning(f"Operação lenta: {self.operation_name} ({duration:.2f}s)")
        
        self.span.end()

# Uso do monitor
def process_large_dataset(data):
    with PerformanceMonitor("process_large_dataset") as monitor:
        # Operação que queremos monitorar
        time.sleep(0.5)  # Simular processamento
        return len(data) * 2
```

## 🎯 Conclusão

Estes exemplos demonstram como usar o `django-coralogix-otel` em diferentes cenários:

- **Configuração básica** para começar rapidamente
- **Integração completa** com Django (settings, wsgi, asgi)
- **Uso avançado** em views com tracing customizado
- **Configuração Kubernetes** para ambientes de produção
- **Desenvolvimento local** com debugging
- **Testes** para garantir qualidade
- **Troubleshooting** para diagnosticar problemas

Para mais informações, consulte o [README.md](README.md) principal.
