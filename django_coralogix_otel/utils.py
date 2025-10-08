"""
Utilitários para integração OpenTelemetry com Django
Implementação completa com fallbacks e validação robusta
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


def validate_environment_variables() -> bool:
    """
    Valida se todas as variáveis de ambiente necessárias estão definidas
    com suporte completo às variáveis do Kubernetes
    
    Returns:
        bool: True se todas as variáveis necessárias estão presentes
    """
    # Variáveis obrigatórias para funcionamento básico
    required_vars = [
        "CORALOGIX_PRIVATE_KEY",
        "OTEL_EXPORTER_OTLP_ENDPOINT",
    ]
    
    # Variáveis opcionais com valores padrão
    optional_vars = {
        "OTEL_SERVICE_NAME": "django-application",
        "CORALOGIX_APPLICATION_NAME": "django-app",
        "CORALOGIX_SUBSYSTEM_NAME": "backend",
        "OTEL_SERVICE_NAMESPACE": "default",
        "OTEL_SERVICE_VERSION": "1.0.0",
        "OTEL_DEPLOYMENT_ENVIRONMENT": "development",
        "OTEL_PYTHON_DJANGO_INSTRUMENT": "true",
        "OTEL_PYTHON_REQUESTS_INSTRUMENT": "true",
        "OTEL_PYTHON_PSYCOPG2_INSTRUMENT": "true",
        "OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED": "true",
    }
    
    # Verificar variáveis obrigatórias
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        logger.error(f"Variáveis de ambiente obrigatórias ausentes: {missing_required}")
        return False
    
    # Log das variáveis opcionais ausentes
    missing_optional = [var for var in optional_vars if not os.getenv(var)]
    if missing_optional:
        logger.info(f"Usando valores padrão para variáveis opcionais: {missing_optional}")
    
    logger.info("Variáveis de ambiente validadas com sucesso")
    return True


def get_coralogix_headers() -> Dict[str, str]:
    """
    Retorna os headers necessários para comunicação com Coralogix
    com fallbacks para valores padrão
    
    Returns:
        Dict[str, str]: Headers para requisições OTLP
    """
    return {
        "Authorization": f"Bearer {os.getenv('CORALOGIX_PRIVATE_KEY')}",
        "CX-Application-Name": os.getenv("CORALOGIX_APPLICATION_NAME", "django-app"),
        "CX-Subsystem-Name": os.getenv("CORALOGIX_SUBSYSTEM_NAME", "backend"),
    }


def get_resource_attributes() -> Dict[str, str]:
    """
    Retorna os atributos de resource para OpenTelemetry
    com parsing de OTEL_RESOURCE_ATTRIBUTES do Kubernetes
    
    Returns:
        Dict[str, str]: Atributos do resource
    """
    # Atributos base
    attributes = {
        "service.name": os.getenv("OTEL_SERVICE_NAME", "django-application"),
        "service.namespace": os.getenv("OTEL_SERVICE_NAMESPACE", "default"),
        "service.version": os.getenv("OTEL_SERVICE_VERSION", "1.0.0"),
        "deployment.environment": os.getenv("OTEL_DEPLOYMENT_ENVIRONMENT", "development"),
        "coralogix.application": os.getenv("CORALOGIX_APPLICATION_NAME", "django-app"),
        "coralogix.subsystem": os.getenv("CORALOGIX_SUBSYSTEM_NAME", "backend"),
    }
    
    # Adicionar atributos do Kubernetes se disponíveis
    k8s_attributes = _parse_k8s_resource_attributes()
    attributes.update(k8s_attributes)
    
    # Filtrar valores None
    return {k: v for k, v in attributes.items() if v is not None}


def _parse_k8s_resource_attributes() -> Dict[str, str]:
    """
    Parseia a variável OTEL_RESOURCE_ATTRIBUTES do formato Kubernetes
    
    Formato esperado: key1=value1,key2=value2
    
    Returns:
        Dict[str, str]: Atributos parseados
    """
    resource_attrs = os.getenv("OTEL_RESOURCE_ATTRIBUTES", "")
    if not resource_attrs:
        return {}
    
    try:
        attributes = {}
        pairs = resource_attrs.split(',')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                attributes[key.strip()] = value.strip()
        return attributes
    except Exception as e:
        logger.warning(f"Erro ao parsear OTEL_RESOURCE_ATTRIBUTES: {e}")
        return {}


def is_opentelemetry_available() -> bool:
    """
    Verifica se as dependências do OpenTelemetry estão disponíveis
    com fallback para operação sem OpenTelemetry
    
    Returns:
        bool: True se OpenTelemetry estiver disponível
    """
    try:
        import opentelemetry
        import opentelemetry.sdk
        return True
    except ImportError as e:
        logger.warning(f"OpenTelemetry não está disponível: {e}")
        return False


def is_instrumentation_enabled(instrumentation_name: str) -> bool:
    """
    Verifica se uma instrumentação específica está habilitada
    baseado nas variáveis de ambiente do Kubernetes
    
    Args:
        instrumentation_name: Nome da instrumentação (django, requests, etc.)
        
    Returns:
        bool: True se a instrumentação está habilitada
    """
    env_var_name = f"OTEL_PYTHON_{instrumentation_name.upper()}_INSTRUMENT"
    return os.getenv(env_var_name, "true").lower() == "true"


def get_enabled_instrumentations() -> List[str]:
    """
    Retorna a lista de instrumentações habilitadas baseado nas variáveis de ambiente
    
    Returns:
        List[str]: Lista de instrumentações habilitadas
    """
    instrumentations = [
        "django",
        "requests",
        "psycopg2",
        "logging",
        "kafka",
        "wsgi",
        "asgi",
    ]
    
    return [inst for inst in instrumentations if is_instrumentation_enabled(inst)]


def configure_django_settings() -> Dict[str, Any]:
    """
    Configura as settings do Django para OpenTelemetry
    com fallbacks para operação sem OpenTelemetry
    
    Esta função deve ser chamada no settings.py do projeto Django
    
    Returns:
        Dict[str, Any]: Configurações a serem adicionadas ao settings.py
    """
    settings_to_add: Dict[str, Any] = {
        # Adicionar middleware OpenTelemetry se disponível
        'MIDDLEWARE': [
            'django_coralogix_otel.middleware.OpenTelemetryMiddleware',
        ],
    }
    
    # Configurações de logging apenas se OpenTelemetry estiver disponível
    if is_opentelemetry_available():
        settings_to_add['LOGGING'] = {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                'opentelemetry': {
                    'level': 'INFO',
                    'class': 'opentelemetry.sdk._logs.LoggingHandler',
                },
            },
            'root': {
                'level': 'INFO',
                'handlers': ['opentelemetry'],
            },
        }
    
    return settings_to_add


def get_otel_config() -> Dict[str, Any]:
    """
    Retorna a configuração OpenTelemetry baseada em variáveis de ambiente
    
    Returns:
        Dict[str, Any]: Configuração OpenTelemetry
    """
    return {
        'service_name': os.getenv("OTEL_SERVICE_NAME", "django-application"),
        'endpoint': os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
        'environment': os.getenv("OTEL_DEPLOYMENT_ENVIRONMENT", "development"),
        'enable_console_exporter': os.getenv("OTEL_LOG_LEVEL") == "DEBUG",
        'enabled_instrumentations': get_enabled_instrumentations(),
    }


def safe_configure_opentelemetry() -> bool:
    """
    Configuração segura do OpenTelemetry com fallbacks robustos
    
    Returns:
        bool: True se a configuração foi bem-sucedida
    """
    try:
        if not validate_environment_variables():
            logger.warning("Configuração de ambiente inválida, OpenTelemetry não será configurado")
            return False
        
        if not is_opentelemetry_available():
            logger.warning("OpenTelemetry não disponível, configuração ignorada")
            return False
        
        from .config import configure_opentelemetry
        return configure_opentelemetry()
        
    except Exception as e:
        logger.error(f"Erro seguro ao configurar OpenTelemetry: {e}")
        return False