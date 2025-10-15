# 🛠️ Tarefas de Correção - Django Coralogix OpenTelemetry

## 🚨 **PRIORIDADE 1 - CORREÇÕES CRÍTICAS**

### **1. Middleware OpenTelemetry - Correção de Tipos**
**Arquivo**: `django_coralogix_otel/middleware.py`

#### **Problema Identificado:**
```python
# Linha 27: current_span.set_attribute("request", request)
# Erro: ASGIRequest não é suportado como atributo OpenTelemetry
```

#### **Correção Necessária:**
```python
def _safe_set_attribute(span, key, value):
    """Define atributo de forma segura, convertendo tipos complexos."""
    if isinstance(value, (str, int, float, bool, type(None))):
        span.set_attribute(key, value)
    elif isinstance(value, (dict, list, tuple)):
        span.set_attribute(key, str(value))
    # Ignorar tipos complexos como ASGIRequest

def __call__(self, request):
    current_span = trace.get_current_span()

    if current_span and current_span.is_recording():
        # HTTP Attributes (seguros)
        current_span.set_attribute("http.method", request.method)
        current_span.set_attribute("http.url", request.build_absolute_uri())
        current_span.set_attribute("http.scheme", request.scheme)
        current_span.set_attribute("http.host", request.get_host())
        current_span.set_attribute("http.user_agent", request.META.get("HTTP_USER_AGENT", ""))
        current_span.set_attribute("http.remote_addr", self.get_client_ip(request))
        current_span.set_attribute("http.target", request.path)

        # Django Attributes (seguros)
        current_span.set_attribute("django.user.id", self.get_user_id(request))
        current_span.set_attribute("django.user.username", self.get_username(request))
        current_span.set_attribute("django.session.id", self.get_session_id(request))

        # NUNCA passar o objeto request inteiro
        # REMOVIDO: current_span.set_attribute("request", request)
```

### **2. Validação de Funcionalidade no Startup**
**Arquivo**: `django_coralogix_otel/otel_config.py`

#### **Adicionar após linha 153:**
```python
def verify_traces_health():
    """Verifica se traces estão funcionando corretamente."""
    try:
        from opentelemetry import trace
        tracer = trace.get_tracer("health-check")

        with tracer.start_as_current_span("otel-health-check") as span:
            span.set_attribute("health.check", "success")
            span.set_attribute("otel.version", trace.__version__)
            return True

    except Exception as e:
        logger.error(f"❌ OpenTelemetry health check failed: {e}")
        return False

def verify_metrics_health():
    """Verifica se métricas estão funcionando."""
    try:
        from opentelemetry import metrics
        meter = metrics.get_meter("health-check")
        counter = meter.create_counter("health.check.counter")
        counter.add(1, {"status": "ok"})
        return True

    except Exception as e:
        logger.error(f"❌ Metrics health check failed: {e}")
        return False
```

#### **Modificar função `configure_opentelemetry()` (após linha 201):**
```python
    # Verificação de saúde das integrações
    if not verify_traces_health():
        logger.warning("⚠️ Traces verification failed - check configuration")

    if not verify_metrics_health():
        logger.warning("⚠️ Metrics verification failed - check configuration")
```

---

## ⚡ **PRIORIDADE 2 - MELHORIAS IMPORTANTES**

### **3. Logging de Segurança Aprimorado**
**Arquivo**: `django_coralogix_otel/simple_logging.py`

#### **Adicionar tratamento de exceções:**
```python
def setup_json_logging():
    """Setup JSON logging com OpenTelemetry - versão segura."""
    try:
        root_logger = logging.getLogger()

        # Remover handlers existentes para evitar duplicatas
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler):
                root_logger.removeHandler(handler)

        # Configurar novo handler JSON
        handler = logging.StreamHandler()
        formatter = OpenTelemetryJSONFormatter()
        handler.setFormatter(formatter)

        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

    except Exception as e:
        # Fallback para logging básico se JSON falhar
        logging.basicConfig(level=logging.INFO)
        logger.error(f"❌ JSON logging setup failed: {e}")
```

### **4. Documentação de Configuração**
**Arquivo**: `docs/KAFKA_INTEGRATION.md` (novo)

#### **Conteúdo:**
```markdown
# 📡 Integração Kafka com OpenTelemetry

## Configuração necessária:

```bash
# environment variables
OTEL_PYTHON_KAFKA_PYTHON_INSTRUMENT=true
OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://$(OTEL_IP):4317
```

## Verificação:

```python
# Verificar se kafka-python está instrumentado
from opentelemetry.instrumentation.kafka import KafkaInstrumentor
# Deve funcionar sem erros
```
```

---

## 📋 **CHECKLIST DE IMPLEMENTAÇÃO**

### **Para cada correção:**

- [ ] ✅ Implementar correção no código
- [ ] ✅ Adicionar testes unitários
- [ ] ✅ Atualizar documentação
- [ ] ✅ Testar localmente
- [ ] ✅ Deploy em staging
- [ ] ✅ Validar em produção

### **Validação pós-correção:**

```bash
# 1. Verificar logs de erro ASGIRequest
kubectl logs deployment/vert-issue-prd-back | grep "ASGIRequest"

# 2. Verificar traces no Coralogix
# Deve ver spans com serviceName "vert-issue-prd"

# 3. Verificar performance
# Medir latência antes/depois das correções
```

---

## 🧪 **TESTES AUTOMATIZADOS**

### **Novo arquivo**: `tests/test_middleware_fix.py`
```python
import pytest
from django.test import TestCase
from unittest.mock import Mock, patch
from django_coralogix_otel.middleware import OpenTelemetryMiddleware

class TestMiddlewareFixes(TestCase):
    def test_asgi_request_not_set_as_attribute(self):
        """Testa que objeto request não é setado como atributo."""
        mock_get_response = Mock()
        middleware = OpenTelemetryMiddleware(mock_get_response)

        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.build_absolute_uri.return_value = "http://test.com"

        with patch('django_coralogix_otel.middleware.trace.get_current_span') as mock_span:
            mock_span.return_value = Mock()
            mock_span.return_value.is_recording.return_value = True

            middleware(mock_request)

            # Verificar que set_attribute foi chamado apenas com tipos seguros
            safe_calls = ['http.method', 'http.url', 'http.scheme']
            for call in mock_span.return_value.set_attribute.call_args_list:
                assert call[0] in safe_calls
                assert not isinstance(call[1], Mock)  # Não deve ser Mock (ASGIRequest)
```

---

## 📊 **MÉTRICAS DE SUCESSO**

### **Antes das Correções:**
- ❌ Taxa de erro ASGIRequest: 100%
- ❌ Traces enviados: 0%
- ✅ Logs funcionais: 100%
- ✅ Métricas HTTP: 100%

### **Após Correções (Meta):**
- ✅ Taxa de erro ASGIRequest: 0%
- ✅ Traces enviados: >95%
- ✅ Logs funcionais: 100%
- ✅ Métricas HTTP: 100%
- 🎯 Performance impact: <5%

---

**Status**: 🟡 **AGUARDANDO IMPLEMENTAÇÃO**