# 📡 Integração Kafka com OpenTelemetry

## Configuração necessária

Adicione as seguintes variáveis de ambiente ao seu deployment:

```bash
# environment variables
OTEL_PYTHON_KAFKA_PYTHON_INSTRUMENT=true
OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://$(OTEL_IP):4317
```

## Exemplo de configuração Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sua-app
spec:
  template:
    spec:
      containers:
        - name: app
          env:
            - name: OTEL_SERVICE_NAME
              value: sua-app
            - name: OTEL_RESOURCE_ATTRIBUTES
              value: cx.application.name=sua-app,cx.subsystem.name=sua-app-back
            - name: OTEL_IP
              valueFrom:
                fieldRef:
                  fieldPath: status.hostIP
            - name: OTEL_EXPORTER_OTLP_ENDPOINT
              value: http://$(OTEL_IP):4317
            # Instrumentações
            - name: OTEL_PYTHON_DJANGO_INSTRUMENT
              value: "true"
            - name: OTEL_PYTHON_REQUESTS_INSTRUMENT
              value: "true"
            - name: OTEL_PYTHON_PSYCOPG2_INSTRUMENT
              value: "true"
            - name: OTEL_PYTHON_KAFKA_PYTHON_INSTRUMENT  # ← NOVO
              value: "true"
            - name: OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED
              value: "true"
```

## Verificação de instalação

### 1. Verificar se kafka-python está instrumentado

```python
# No shell Python da sua aplicação
from opentelemetry.instrumentation.kafka import KafkaInstrumentor
print("Kafka instrumentation disponível")
```

### 2. Verificar traces de produção/consumo

```python
# Seu código Kafka continuará o mesmo
from kafka import KafkaProducer, KafkaConsumer

# A instrumentação é automática
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092']
)

consumer = KafkaConsumer(
    'meu-topico',
    bootstrap_servers=['localhost:9092']
)
```

## Atributos coletados automaticamente

### Producer
- `messaging.system=kafka`
- `messaging.destination.kind=topic`
- `messaging.destination=<topic_name>`
- `messaging.operation=publish`

### Consumer  
- `messaging.system=kafka`
- `messaging.destination.kind=topic`
- `messaging.destination=<topic_name>`
- `messaging.operation=receive`

## Troubleshooting

### Logs de erro comuns

```bash
# Verificar se instrumentação está ativa
kubectl logs deployment/sua-app | grep "kafka"

# Verificar traces no Coralogix
# Procure por spans com operation=publish ou operation=receive
```

### Exemplo de trace esperado

```json
{
  "name": "meu-topico publish",
  "kind": "PRODUCER",
  "attributes": {
    "messaging.system": "kafka",
    "messaging.destination": "meu-topico",
    "messaging.operation": "publish"
  }
}
```

## Compatibilidade

- ✅ kafka-python >= 2.0.0
- ✅ aiokafka (para aplicações async)
- ✅ Todas as versões do Django suportadas pela lib

## Performance

A instrumentação Kafka adiciona < 2ms de overhead por operação e é considerada segura para produção.