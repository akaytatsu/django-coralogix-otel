"""
Exemplo de uso do pacote django-coralogix-otel

Este exemplo demonstra como integrar o pacote em um projeto Django
para habilitar a instrumentação automática OpenTelemetry com Coralogix.
"""

import os
import logging
from django.conf import settings

# Configurar variáveis de ambiente para exemplo
os.environ.update({
    "CORALOGIX_PRIVATE_KEY": "your-coralogix-private-key",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "https://ingress.coralogix.com:443",
    "OTEL_SERVICE_NAME": "my-django-app",
    "CORALOGIX_APPLICATION_NAME": "my-application",
    "CORALOGIX_SUBSYSTEM_NAME": "backend",
    "OTEL_DEPLOYMENT_ENVIRONMENT": "production",
    "DJANGO_CORALOGIX_AUTO_INIT": "true",
})

# Exemplo 1: Uso básico no settings.py do Django
def configure_django_settings():
    """
    Configuração recomendada para o settings.py do Django
    """
    
    # Importar utilitários do pacote
    from django_coralogix_otel import configure_django_settings
    
    # Obter configurações automáticas
    otel_settings = configure_django_settings()
    
    # Adicionar ao settings.py existente
    settings.MIDDLEWARE = otel_settings['MIDDLEWARE'] + settings.MIDDLEWARE
    
    if 'LOGGING' in otel_settings:
        settings.LOGGING = otel_settings['LOGGING']


# Exemplo 2: Inicialização manual no wsgi.py
def configure_wsgi():
    """
    Configuração recomendada para o wsgi.py do Django
    """
    import os
    from django.core.wsgi import get_wsgi_application
    
    # Inicializar OpenTelemetry antes da aplicação Django
    from django_coralogix_otel import initialize_opentelemetry
    
    if initialize_opentelemetry():
        print("OpenTelemetry inicializado com sucesso")
    else:
        print("OpenTelemetry não pôde ser inicializado, continuando sem telemetria")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    application = get_wsgi_application()


# Exemplo 3: Uso em views Django
def example_view(request):
    """
    Exemplo de view Django com instrumentação automática
    """
    from django.http import JsonResponse
    from django_coralogix_otel import get_tracer
    
    # Obter tracer para criar spans manuais
    tracer = get_tracer("myapp.views")
    
    with tracer.start_as_current_span("processar_dados") as span:
        span.set_attribute("user.id", request.user.id if request.user.is_authenticated else "anonymous")
        
        # Sua lógica de negócio aqui
        data = {"status": "success", "message": "Dados processados"}
        
        span.set_attribute("result.size", len(str(data)))
        
        return JsonResponse(data)


# Exemplo 4: Configuração para Kubernetes
def kubernetes_example():
    """
    Exemplo de configuração para ambiente Kubernetes
    """
    # Variáveis de ambiente típicas do Kubernetes
    kubernetes_env = {
        "OTEL_SERVICE_NAME": "my-django-app",
        "OTEL_RESOURCE_ATTRIBUTES": "k8s.namespace=production,k8s.pod.name=myapp-pod-123",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "https://ingress.coralogix.com:443",
        "OTEL_PYTHON_DJANGO_INSTRUMENT": "true",
        "OTEL_PYTHON_REQUESTS_INSTRUMENT": "true",
        "OTEL_PYTHON_PSYCOPG2_INSTRUMENT": "true",
        "OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED": "true",
        "CORALOGIX_PRIVATE_KEY": "your-coralogix-key",
        "CORALOGIX_APPLICATION_NAME": "my-application",
        "CORALOGIX_SUBSYSTEM_NAME": "backend",
    }
    
    os.environ.update(kubernetes_env)
    
    # Inicialização automática
    from django_coralogix_otel import auto_initialize
    if auto_initialize():
        print("OpenTelemetry configurado para Kubernetes")
    else:
        print("Configuração Kubernetes falhou")


# Exemplo 5: Uso avançado com instrumentação híbrida
def advanced_usage():
    """
    Exemplo de uso avançado com estratégia híbrida
    """
    from django_coralogix_otel import (
        hybrid_instrumentation,
        get_enabled_instrumentations,
        get_otel_config
    )
    
    # Verificar configuração atual
    config = get_otel_config()
    print(f"Configuração OpenTelemetry: {config}")
    
    # Verificar instrumentações habilitadas
    enabled_inst = get_enabled_instrumentations()
    print(f"Instrumentações habilitadas: {enabled_inst}")
    
    # Aplicar instrumentação híbrida
    if hybrid_instrumentation():
        print("Instrumentação híbrida aplicada com sucesso")
    else:
        print("Falha na instrumentação híbrida")


# Exemplo 6: Tratamento de erros e fallbacks
def error_handling_example():
    """
    Exemplo de tratamento robusto de erros
    """
    from django_coralogix_otel import safe_configure_opentelemetry
    
    # Configuração segura com fallbacks
    if safe_configure_opentelemetry():
        print("OpenTelemetry configurado com sucesso")
    else:
        print("OpenTelemetry não disponível, aplicação continua funcionando normalmente")
        
        # Log alternativo sem OpenTelemetry
        logging.info("Aplicação rodando sem telemetria OpenTelemetry")


if __name__ == "__main__":
    # Executar exemplos
    print("=== Exemplo de uso django-coralogix-otel ===")
    
    print("\n1. Configuração Kubernetes:")
    kubernetes_example()
    
    print("\n2. Uso avançado:")
    advanced_usage()
    
    print("\n3. Tratamento de erros:")
    error_handling_example()
    
    print("\n=== Exemplos concluídos ===")