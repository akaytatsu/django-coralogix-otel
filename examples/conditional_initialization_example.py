"""
Exemplo de uso da inicialização condicional do OpenTelemetry
Demonstra como usar as novas funções para evitar problemas de inicialização prematura
"""

import os
import sys
import logging

# Configurar logging para debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_django_environment():
    """Configura o ambiente Django para o exemplo"""
    # Definir settings module se não estiver definido
    if not os.getenv('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.settings')
    
    try:
        import django
        django.setup()
        logger.info("Django configurado com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao configurar Django: {e}")
        return False

def example_conditional_initialization():
    """Exemplo de inicialização condicional"""
    print("=== Exemplo de Inicialização Condicional OpenTelemetry ===")
    
    # Verificar se o Django está configurado
    from django_coralogix_otel import is_django_configured
    
    if not is_django_configured():
        print("❌ Django não está configurado. Configurando ambiente...")
        if not setup_django_environment():
            print("❌ Falha ao configurar Django. Abortando inicialização OpenTelemetry.")
            return False
    
    # Agora tentar inicialização condicional
    from django_coralogix_otel import conditional_initialize_opentelemetry
    
    print("🔄 Tentando inicialização condicional do OpenTelemetry...")
    success = conditional_initialize_opentelemetry(enable_console_exporter=True)
    
    if success:
        print("✅ OpenTelemetry inicializado com sucesso!")
        
        # Verificar status da inicialização
        from django_coralogix_otel import get_initialization_status
        status = get_initialization_status()
        print(f"📊 Status da inicialização: {status}")
        
        # Aplicar instrumentação híbrida
        from django_coralogix_otel import hybrid_instrumentation
        hybrid_success = hybrid_instrumentation()
        print(f"🎯 Instrumentação híbrida: {'✅ Sucesso' if hybrid_success else '❌ Falha'}")
        
    else:
        print("❌ Falha na inicialização condicional do OpenTelemetry")
        
    return success

def example_delayed_auto_initialize():
    """Exemplo de inicialização automática atrasada"""
    print("\n=== Exemplo de Inicialização Automática Atrasada ===")
    
    # Configurar variável de ambiente para auto-inicialização
    os.environ['DJANGO_CORALOGIX_AUTO_INIT'] = 'true'
    
    # Configurar Django primeiro
    if not setup_django_environment():
        print("❌ Falha ao configurar Django")
        return False
    
    # Agora chamar a inicialização automática atrasada
    from django_coralogix_otel import delayed_auto_initialize
    
    print("🔄 Executando inicialização automática atrasada...")
    success = delayed_auto_initialize()
    
    if success:
        print("✅ Inicialização automática atrasada bem-sucedida!")
    else:
        print("❌ Falha na inicialização automática atrasada")
        
    return success

def example_without_django_configuration():
    """Exemplo demonstrando comportamento sem configuração Django"""
    print("\n=== Exemplo sem Configuração Django ===")
    
    # Limpar configuração Django
    if 'DJANGO_SETTINGS_MODULE' in os.environ:
        del os.environ['DJANGO_SETTINGS_MODULE']
    
    from django_coralogix_otel import is_django_configured, conditional_initialize_opentelemetry
    
    print("🔍 Verificando configuração Django...")
    django_configured = is_django_configured()
    print(f"📋 Django configurado: {django_configured}")
    
    if not django_configured:
        print("⚠️  Django não configurado - inicialização será adiada")
        
        # Tentar inicialização condicional mesmo sem Django configurado
        print("🔄 Tentando inicialização condicional sem Django configurado...")
        success = conditional_initialize_opentelemetry()
        print(f"📊 Resultado: {'✅ Sucesso' if success else '❌ Falha (esperado)'}")
        
        if not success:
            print("💡 Comportamento esperado: OpenTelemetry não inicializa sem Django configurado")

if __name__ == "__main__":
    print("🧪 Testando inicialização condicional do OpenTelemetry")
    print("=" * 60)
    
    # Exemplo 1: Inicialização condicional
    example_conditional_initialization()
    
    # Exemplo 2: Inicialização automática atrasada
    example_delayed_auto_initialize()
    
    # Exemplo 3: Comportamento sem configuração Django
    example_without_django_configuration()
    
    print("\n" + "=" * 60)
    print("🧪 Testes concluídos!")
    print("\n📝 Resumo das correções implementadas:")
    print("✅ Removida auto-inicialização prematura no import")
    print("✅ Adicionada inicialização condicional")
    print("✅ Validação de configuração Django antes da inicialização")
    print("✅ Verificação de DATABASES e ALLOWED_HOSTS")
    print("✅ Logs informativos para debugging")
    print("✅ Compatibilidade mantida com deployments existentes")