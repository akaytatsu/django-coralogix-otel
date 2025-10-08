# Troubleshooting - django-coralogix-otel

Este guia fornece soluções para problemas comuns encontrados ao usar o pacote `django-coralogix-otel`.

## 📋 Índice

1. [Problemas de Inicialização](#problemas-de-inicialização)
2. [Problemas de Configuração](#problemas-de-configuração)
3. [Problemas de Instrumentação](#problemas-de-instrumentação)
4. [Problemas de Performance](#problemas-de-performance)
5. [Problemas de Kubernetes](#problemas-de-kubernetes)
6. [Logs e Debugging](#logs-e-debugging)
7. [Boas Práticas](#boas-práticas)

## 🔧 Problemas de Inicialização

### OpenTelemetry não inicializa

**Sintomas:**
- Logs mostram "OpenTelemetry não inicializado"
- Traces não aparecem no Coralogix
- Aplicação funciona normalmente, mas sem telemetria

**Soluções:**

1. **Verificar variáveis de ambiente obrigatórias:**
```python
from django_coralogix_otel import validate_environment_variables

if not validate_environment_variables():
    print("❌ Variáveis obrigatórias ausentes")
```

2. **Verificar disponibilidade do OpenTelemetry:**
```python
from django_coralogix_otel import is_opentelemetry_available

if not is_opentelemetry_available():
    print("❌ OpenTelemetry não está instalado")
    # Instalar: pip install opentelemetry-sdk opentelemetry-exporter-otlp
```

3. **Forçar inicialização manual:**
```python
from django_coralogix_otel import initialize_opentelemetry

# No wsgi.py ou asgi.py
if initialize_opentelemetry(enable_console_exporter=True):
    print("✅ OpenTelemetry inicializado")
else:
    print("❌ Falha na inicialização")
```

### Middleware não está funcionando

**Sintomas:**
- Requests não aparecem com spans no Coralogix
- Atributos customizados não estão presentes

**Soluções:**

1. **Verificar ordem do middleware:**
```python
# settings.py - O middleware deve estar no início
MIDDLEWARE = [
    'django_coralogix_otel.middleware.OpenTelemetryMiddleware',
    # ... outros middlewares
]
```

2. **Verificar se o middleware está habilitado:**
```bash
# Variável de ambiente
OTEL_PYTHON_DJANGO_INSTRUMENT=true
```

3. **Testar manualmente o middleware:**
```python
# test_middleware.py
from django.test import RequestFactory
from django_coralogix_otel.middleware import OpenTelemetryMiddleware

def test_middleware():
    factory = RequestFactory()
    request = factory.get('/test')
    
    middleware = OpenTelemetryMiddleware(lambda r: None)
    response = middleware(request)
    
    print("✅ Middleware testado")
```

## ⚙️ Problemas de Configuração

### Variáveis de ambiente não são detectadas

**Sintomas:**
- Configurações padrão são usadas mesmo com variáveis definidas
- Atributos Coralogix incorretos

**Soluções:**

1. **Verificar carregamento das variáveis:**
```python
import os
print(f"CORALOGIX_PRIVATE_KEY: {'***' if os.getenv('CORALOGIX_PRIVATE_KEY') else 'AUSENTE'}")
print(f"OTEL_SERVICE_NAME: {os.getenv('OTEL_SERVICE_NAME', 'NÃO DEFINIDO')}")
```

2. **Usar valores padrão explícitos:**
```python
from django_coralogix_otel import configure_django_settings

# Forçar configuração específica
os.environ.setdefault('OTEL_SERVICE_NAME', 'meu-app')
os.environ.setdefault('CORALOGIX_APPLICATION_NAME', 'minha-aplicacao')
```

3. **Verificar arquivo .env (se usado):**
```bash
# .env
CORALOGIX_PRIVATE_KEY=seu-token
OTEL_EXPORTER_OTLP_ENDPOINT=https://ingress.coralogix.com:443
OTEL_SERVICE_NAME=meu-app
```

### Endpoint OTLP incorreto

**Sintomas:**
- Traces não chegam ao Coralogix
- Erros de conexão nos logs

**Soluções:**

1. **Verificar endpoint:**
```python
endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
print(f"Endpoint: {endpoint}")
# Deve ser: https://ingress.coralogix.com:443
```

2. **Testar conectividade:**
```python
import requests

try:
    response = requests.get('https://ingress.coralogix.com:443', timeout=5)
    print(f"✅ Endpoint acessível: {response.status_code}")
except Exception as e:
    print(f"❌ Endpoint inacessível: {e}")
```

3. **Usar endpoint alternativo para desenvolvimento:**
```python
# Para desenvolvimento, usar console exporter
from django_coralogix_otel import initialize_opentelemetry
initialize_opentelemetry(enable_console_exporter=True)
```

## 🎯 Problemas de Instrumentação

### Instrumentações específicas não funcionam

**Sintomas:**
- PostgreSQL queries não aparecem
- Requests HTTP externos não são rastreados
- Logs não são enviados

**Soluções:**

1. **Verificar instrumentações habilitadas:**
```python
from django_coralogix_otel import get_enabled_instrumentations

enabled = get_enabled_instrumentations()
print(f"Instrumentações habilitadas: {enabled}")
```

2. **Habilitar instrumentações específicas:**
```bash
# PostgreSQL
OTEL_PYTHON_PSYCOPG2_INSTRUMENT=true

# Requests HTTP
OTEL_PYTHON_REQUESTS_INSTRUMENT=true

# Logging
OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
```

3. **Verificar dependências:**
```bash
# Instalar instrumentações específicas
pip install opentelemetry-instrumentation-psycopg2
pip install opentelemetry-instrumentation-requests
pip install opentelemetry-instrumentation-logging
```

### Spans customizados não aparecem

**Sintomas:**
- Spans manuais criados com `get_tracer()` não são visíveis
- Atributos customizados faltando

**Soluções:**

1. **Verificar criação de spans:**
```python
from django_coralogix_otel import get_tracer

def minha_view(request):
    tracer = get_tracer("minhaapp.views")
    
    with tracer.start_as_current_span("meu_span") as span:
        span.set_attribute("custom.attribute", "valor")
        # ... código
        print("✅ Span criado")
```

2. **Verificar se OpenTelemetry está ativo:**
```python
from django_coralogix_otel import get_initialization_status

if get_initialization_status():
    print("✅ OpenTelemetry ativo - spans serão enviados")
else:
    print("❌ OpenTelemetry inativo - spans não serão enviados")
```

3. **Usar console exporter para debug:**
```python
# Inicializar com console exporter
initialize_opentelemetry(enable_console_exporter=True)
# Spans aparecerão no console
```

## ⚡ Problemas de Performance

### Aplicação ficou mais lenta

**Sintomas:**
- Tempo de resposta aumentou significativamente
- Alta utilização de CPU/memória

**Soluções:**

1. **Reduzir sampling rate:**
```bash
# Configurar sampling (se suportado)
OTEL_TRACES_SAMPLER=parentbased_always_on
OTEL_TRACES_SAMPLER_ARG=0.1  # 10% dos traces
```

2. **Desabilitar instrumentações não essenciais:**
```bash
# Desabilitar instrumentações pesadas se necessário
OTEL_PYTHON_PSYCOPG2_INSTRUMENT=false
OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=false
```

3. **Otimizar atributos:**
```python
# Evitar atributos muito grandes
span.set_attribute("user.id", user.id)  # ✅ Bom
span.set_attribute("user.data", str(user.__dict__))  # ❌ Ruim (muito grande)
```

4. **Usar batch processing:**
```python
# O pacote já usa batch processing por padrão
# Configurações podem ser ajustadas via variáveis de ambiente
OTEL_BSP_SCHEDULE_DELAY=5000  # 5 segundos
OTEL_BSP_MAX_QUEUE_SIZE=2048
OTEL_BSP_MAX_EXPORT_BATCH_SIZE=512
```

### Alto uso de memória

**Sintomas:**
- Aplicação consome mais memória que o normal
- GC frequente

**Soluções:**

1. **Ajustar configurações de batch:**
```bash
# Reduzir tamanho do batch
OTEL_BSP_MAX_QUEUE_SIZE=1024
OTEL_BSP_MAX_EXPORT_BATCH_SIZE=256
```

2. **Monitorar métricas de memory:**
```python
import psutil
import logging

def log_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    logging.info(f"Uso de memória: {memory_info.rss / 1024 / 1024:.2f} MB")
```

3. **Verificar memory leaks:**
```python
# Usar memory profiler para identificar leaks
# pip install memory-profiler
```

## ☸️ Problemas de Kubernetes

### Variáveis de ambiente do Kubernetes não funcionam

**Sintomas:**
- Atributos Kubernetes faltando nos spans
- POD_NAME, namespace não detectados

**Soluções:**

1. **Verificar ConfigMap:**
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: django-opentelemetry
data:
  OTEL_RESOURCE_ATTRIBUTES: "k8s.namespace=production,k8s.pod.name=$(POD_NAME)"
```

2. **Verificar deployment:**
```yaml
# k8s/deployment.yaml
spec:
  template:
    spec:
      containers:
      - name: django-app
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
```

3. **Testar variáveis no pod:**
```bash
# Executar no pod
kubectl exec -it <pod-name> -- printenv | grep -E "(POD_NAME|KUBERNETES)"
```

### Sidecar não se comunica

**Sintomas:**
- Traces não são enviados
- Erros de conexão

**Soluções:**

1. **Verificar service mesh configuration:**
```yaml
# Se usando service mesh como Istio
annotations:
  sidecar.istio.io/inject: "true"
```

2. **Verificar network policies:**
```yaml
# Permitir tráfego para Coralogix
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-coralogix
spec:
  egress:
  - to:
    - ipBlock:
        cidr: 52.xx.xx.xx/32  # IPs do Coralogix
    ports:
    - protocol: TCP
      port: 443
```

3. **Testar conectividade do pod:**
```bash
# Executar no pod
kubectl exec -it <pod-name> -- curl -v https://ingress.coralogix.com:443
```

## 📊 Logs e Debugging

### Habilitar logs detalhados

```python
import logging

# Configurar logging para OpenTelemetry
logging.getLogger('django_coralogix_otel').setLevel(logging.DEBUG)
logging.getLogger('opentelemetry').setLevel(logging.DEBUG)

# Configurar formato
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Script de diagnóstico automático

```python
# diagnose.py
from django_coralogix_otel import (
    validate_environment_variables,
    get_initialization_status,
    get_enabled_instrumentations,
    is_opentelemetry_available
)

def diagnose():
    print("🔍 Diagnóstico OpenTelemetry")
    
    checks = [
        ("OpenTelemetry disponível", is_opentelemetry_available()),
        ("Variáveis de ambiente", validate_environment_variables()),
        ("OpenTelemetry inicializado", get_initialization_status()),
    ]
    
    for check_name, status in checks:
        icon = "✅" if status else "❌"
        print(f"{icon} {check_name}")
    
    print(f"📊 Instrumentações: {get_enabled_instrumentations()}")

diagnose()
```

### Monitorar métricas de exportação

```python
from opentelemetry import metrics

meter = metrics.get_meter("export.metrics")
export_counter = meter.create_counter(
    "otel_export_attempts",
    description="Número de tentativas de exportação"
)

error_counter = meter.create_counter(
    "otel_export_errors", 
    description="Número de erros de exportação"
)
```

## 🏆 Boas Práticas

### Configuração de Produção

```python
# settings.py - Configurações recomendadas para produção
os.environ.update({
    "OTEL_LOG_LEVEL": "INFO",  # Não usar DEBUG em produção
    "OTEL_BSP_SCHEDULE_DELAY": "5000",  # 5 segundos
    "OTEL_BSP_MAX_QUEUE_SIZE": "2048",
    "OTEL_BSP_MAX_EXPORT_BATCH_SIZE": "512",
    "OTEL_ATTRIBUTE_COUNT_LIMIT": "128",  # Limitar atributos
    "OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT": "4096",  # Limitar tamanho
})
```

### Configuração de Desenvolvimento

```python
# development.py - Configurações para desenvolvimento
os.environ.update({
    "OTEL_LOG_LEVEL": "DEBUG",
    "DJANGO_CORALOGIX_AUTO_INIT": "true",
    "OTEL_PYTHON_DJANGO_INSTRUMENT": "true",
    "OTEL_PYTHON_REQUESTS_INSTRUMENT": "true",
})
```

### Nomenclatura de Spans

```python
# ✅ Boas práticas para nomes de spans
tracer.start_as_current_span("http.request")  # ✅ Específico
tracer.start_as_current_span("database.query")  # ✅ Descritivo
tracer.start_as_current_span("span")  # ❌ Genérico demais
```

### Atributos Recomendados

```python
# Atributos úteis para todos os spans
span.set_attribute("service.name", "meu-servico")
span.set_attribute("deployment.environment", "production")
span.set_attribute("user.id", user_id)
span.set_attribute("operation.type", "read|write|update|delete")
```

### Monitoramento de Saúde

```python
# health_check.py
from django_coralogix_otel import get_initialization_status
from django.http import JsonResponse

def health_check(request):
    status = {
        "status": "healthy",
        "opentelemetry": get_initialization_status(),
        "timestamp": datetime.now().isoformat()
    }
    
    if not status["opentelemetry"]:
        status["status"] = "degraded"
        status["message"] = "OpenTelemetry não está funcionando"
    
    return JsonResponse(status)
```

## 🆘 Suporte Adicional

Se você ainda estiver com problemas:

1. **Verifique a documentação oficial:**
   - [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
   - [Coralogix Documentation](https://coralogix.com/docs/)

2. **Coletar informações para suporte:**
```python
# collect_debug_info.py
import platform
import sys
from django_coralogix_otel import get_otel_config

debug_info = {
    "python_version": sys.version,
    "platform": platform.platform(),
    "otel_config": get_otel_config(),
    "environment_vars": {
        k: v for k, v in os.environ.items() 
        if k.startswith(('OTEL_', 'CORALOGIX_'))
    }
}

print("Informações de debug:")
import json
print(json.dumps(debug_info, indent=2))
```

3. **Abrir issue no GitHub:**
   - Inclua as informações de debug
   - Descreva os passos para reproduzir
   - Inclua logs relevantes

---

**Lembre-se:** O pacote é projetado para fallback gracioso. Se OpenTelemetry falhar, sua aplicação Django continuará funcionando normalmente, apenas sem telemetria.