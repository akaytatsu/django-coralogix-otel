"""
Entrypoint para inicialização automática do OpenTelemetry
Implementação completa com estratégia híbrida (auto-instrumentação + manual)
"""

import os
import logging
from typing import Optional, List

from .config import configure_opentelemetry
from .utils import (
    validate_environment_variables,
    is_opentelemetry_available,
    get_enabled_instrumentations,
    safe_configure_opentelemetry
)

logger = logging.getLogger(__name__)


def initialize_opentelemetry(enable_console_exporter: bool = False) -> bool:
    """
    Inicializa automaticamente o OpenTelemetry para a aplicação Django
    com estratégia híbrida (auto-instrumentação + configuração manual)
    
    Esta função deve ser chamada no início da aplicação, preferencialmente
    no arquivo settings.py ou wsgi.py do projeto Django.
    
    Args:
        enable_console_exporter: Se True, habilita exportador console para desenvolvimento
        
    Returns:
        bool: True se a inicialização foi bem-sucedida
    """
    logger.info("Iniciando inicialização do OpenTelemetry com estratégia híbrida")
    
    # Configuração segura do OpenTelemetry
    if not safe_configure_opentelemetry():
        logger.warning("Configuração OpenTelemetry falhou, continuando sem telemetria")
        return False
    
    try:
        # Configurar OpenTelemetry com opção de console
        configure_opentelemetry(enable_console_exporter=enable_console_exporter)
        
        # Aplicar instrumentações automáticas baseadas em configuração
        _apply_auto_instrumentation()
        
        logger.info("OpenTelemetry inicializado com sucesso para Coralogix (estratégia híbrida)")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao inicializar OpenTelemetry: {e}")
        return False


def _apply_auto_instrumentation():
    """
    Aplica instrumentações automáticas baseadas nas variáveis de ambiente
    usando a estratégia híbrida (auto-instrumentação + manual)
    """
    enabled_instrumentations = get_enabled_instrumentations()
    
    if not enabled_instrumentations:
        logger.info("Nenhuma instrumentação habilitada por configuração")
        return
    
    logger.info(f"Aplicando instrumentações automáticas: {enabled_instrumentations}")
    
    # Aplicar instrumentação automática geral se disponível
    _apply_general_auto_instrumentation()
    
    # Aplicar instrumentações específicas manualmente
    _apply_specific_instrumentations(enabled_instrumentations)


def _apply_general_auto_instrumentation():
    """
    Aplica instrumentação automática geral se disponível
    """
    try:
        from opentelemetry.instrumentation.auto_instrumentation import instrument
        instrument()
        logger.debug("Instrumentação automática geral aplicada")
    except ImportError:
        logger.debug("Instrumentação automática geral não disponível, usando instrumentações específicas")
    except Exception as e:
        logger.warning(f"Erro ao aplicar instrumentação automática geral: {e}")


def _apply_specific_instrumentations(enabled_instrumentations: List[str]):
    """
    Aplica instrumentações específicas manualmente baseado na configuração
    """
    instrumentation_map = {
        "django": "opentelemetry.instrumentation.django",
        "psycopg2": "opentelemetry.instrumentation.psycopg2",
        "requests": "opentelemetry.instrumentation.requests",
        "logging": "opentelemetry.instrumentation.logging",
        "kafka": "opentelemetry.instrumentation.kafka-python",
        "wsgi": "opentelemetry.instrumentation.wsgi",
        "asgi": "opentelemetry.instrumentation.asgi",
    }
    
    for inst_name in enabled_instrumentations:
        module_name = instrumentation_map.get(inst_name)
        if module_name:
            _apply_specific_instrumentation(module_name, inst_name)


def _apply_specific_instrumentation(module_name: str, inst_name: str):
    """
    Aplica uma instrumentação específica
    """
    try:
        __import__(module_name)
        logger.debug(f"Instrumentação {inst_name} aplicada via {module_name}")
    except ImportError as e:
        logger.warning(f"Instrumentação {inst_name} não disponível: {e}")
    except Exception as e:
        logger.warning(f"Erro ao aplicar instrumentação {inst_name}: {e}")


def auto_initialize() -> bool:
    """
    Inicialização automática baseada em variáveis de ambiente
    com estratégia híbrida
    
    Esta função é chamada automaticamente quando o módulo é importado,
    se a variável de ambiente DJANGO_CORALOGIX_AUTO_INIT estiver definida como "true"
    
    Returns:
        bool: True se a inicialização automática foi bem-sucedida
    """
    auto_init = os.getenv("DJANGO_CORALOGIX_AUTO_INIT", "false").lower()
    
    if auto_init == "true":
        logger.info("Inicialização automática do OpenTelemetry ativada (estratégia híbrida)")
        
        # Verificar se deve habilitar console exporter para desenvolvimento
        enable_console = os.getenv("OTEL_LOG_LEVEL") == "DEBUG" or os.getenv("DJANGO_DEBUG") == "True"
        
        return initialize_opentelemetry(enable_console_exporter=enable_console)
    
    return False


# Inicialização automática quando o módulo é importado
_initialized = auto_initialize()


def get_initialization_status() -> bool:
    """
    Retorna o status da inicialização do OpenTelemetry
    
    Returns:
        bool: True se OpenTelemetry foi inicializado com sucesso
    """
    return _initialized


def instrument_django():
    """
    Instrumenta automaticamente o Django com OpenTelemetry
    usando a estratégia híbrida
    
    Esta função aplica a instrumentação automática para bibliotecas comuns
    baseada nas variáveis de ambiente do Kubernetes
    """
    if not _initialized:
        logger.warning("OpenTelemetry não inicializado. Instrumentação ignorada.")
        return
    
    try:
        _apply_auto_instrumentation()
        logger.info("Instrumentação automática do Django aplicada com sucesso (estratégia híbrida)")
        
    except Exception as e:
        logger.error(f"Erro ao aplicar instrumentação automática: {e}")


def hybrid_instrumentation():
    """
    Função de conveniência para instrumentação híbrida
    Combina auto-instrumentação com configuração manual
    
    Esta função deve ser chamada após a inicialização do Django
    para garantir que todas as bibliotecas estejam disponíveis
    """
    if not _initialized:
        logger.warning("OpenTelemetry não inicializado. Instrumentação híbrida ignorada.")
        return False
    
    try:
        # Aplicar instrumentação automática
        instrument_django()
        
        # Configurações manuais adicionais podem ser adicionadas aqui
        logger.info("Instrumentação híbrida aplicada com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro na instrumentação híbrida: {e}")
        return False


# Exportar funções principais
__all__ = [
    "initialize_opentelemetry",
    "auto_initialize",
    "get_initialization_status",
    "instrument_django",
    "hybrid_instrumentation",
    "safe_configure_opentelemetry",
]