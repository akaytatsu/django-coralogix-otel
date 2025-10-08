#!/usr/bin/env python3
"""
Exemplo de integração do gunicorn.config.py com django-coralogix-otel

Este exemplo demonstra como usar a configuração do Gunicorn otimizada
para OpenTelemetry em conjunto com o pacote django-coralogix-otel.
"""

import os
import sys
import subprocess
from pathlib import Path


def setup_environment():
    """Configurar variáveis de ambiente para exemplo"""
    env_vars = {
        "OTEL_SERVICE_NAME": "django-example-app",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "https://ingress.coralogix.com:443",
        "CORALOGIX_PRIVATE_KEY": "your-private-key-here",
        "OTEL_DEPLOYMENT_ENVIRONMENT": "development",
        "DJANGO_CORALOGIX_AUTO_INIT": "true",
        "OTEL_LOG_LEVEL": "INFO",
        "DJANGO_DEBUG": "True",
        
        # Configurações do Gunicorn
        "GUNICORN_WORKERS": "2",
        "GUNICORN_THREADS": "2",
        "GUNICORN_TIMEOUT": "30",
        "GUNICORN_LOG_LEVEL": "info",
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"✅ {key}={value}")


def check_gunicorn_config():
    """Verificar se o arquivo de configuração do Gunicorn existe"""
    config_path = Path("gunicorn.config.py")
    if config_path.exists():
        print("✅ gunicorn.config.py encontrado")
        return True
    else:
        print("❌ gunicorn.config.py não encontrado")
        return False


def check_entrypoint_script():
    """Verificar se o script de entrypoint existe"""
    entrypoint_path = Path("entrypoint.sh")
    if entrypoint_path.exists():
        print("✅ entrypoint.sh encontrado")
        # Verificar permissões
        if os.access(entrypoint_path, os.X_OK):
            print("✅ entrypoint.sh tem permissão de execução")
        else:
            print("⚠️  entrypoint.sh não tem permissão de execução")
            print("   Execute: chmod +x entrypoint.sh")
        return True
    else:
        print("❌ entrypoint.sh não encontrado")
        return False


def test_gunicorn_config():
    """Testar configuração do Gunicorn"""
    print("\n🧪 Testando configuração do Gunicorn...")
    
    try:
        # Verificar sintaxe do arquivo de configuração
        result = subprocess.run(
            ["python", "-m", "py_compile", "gunicorn.config.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Sintaxe do gunicorn.config.py está correta")
        else:
            print(f"❌ Erro na sintaxe: {result.stderr}")
            return False
            
        # Testar se o arquivo pode ser executado pelo Python
        result = subprocess.run(
            ["python", "-c", "import ast; ast.parse(open('gunicorn.config.py').read())"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ gunicorn.config.py pode ser analisado pelo Python")
        else:
            print(f"❌ Erro na análise: {result.stderr}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar configuração: {e}")
        return False


def generate_sample_wsgi():
    """Gerar arquivo WSGI de exemplo"""
    wsgi_content = '''"""
WSGI config para exemplo de integração
"""

import os
from django_coralogix_otel import initialize_opentelemetry

# Inicializar OpenTelemetry antes da aplicação
initialize_opentelemetry()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
'''

    with open("example_wsgi.py", "w") as f:
        f.write(wsgi_content)
    print("✅ Arquivo example_wsgi.py criado")


def show_usage_examples():
    """Mostrar exemplos de uso"""
    print("\n📋 EXEMPLOS DE USO:")
    
    print("\n1. Usando entrypoint.sh:")
    print("   ./entrypoint.sh gunicorn")
    
    print("\n2. Usando Gunicorn diretamente:")
    print("   opentelemetry-instrument gunicorn --config gunicorn.config.py myproject.wsgi:application")
    
    print("\n3. Com configuração customizada:")
    print("   export GUNICORN_CONFIG=\"--config gunicorn.config.py --bind 0.0.0.0:8080\"")
    print("   ./entrypoint.sh gunicorn")
    
    print("\n4. Para desenvolvimento:")
    print("   ./entrypoint.sh runserver")
    
    print("\n5. Para executar setup:")
    print("   ./entrypoint.sh setup")


def show_docker_example():
    """Mostrar exemplo de Dockerfile"""
    docker_example = '''
# Dockerfile Exemplo
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Copiar scripts de inicialização
COPY entrypoint.sh /usr/local/bin/
COPY gunicorn.config.py /app/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Variáveis de ambiente
ENV DJANGO_CORALOGIX_AUTO_INIT=true
ENV OTEL_LOG_LEVEL=INFO
ENV DJANGO_DEBUG=False
ENV GUNICORN_CONFIG="--config gunicorn.config.py myproject.wsgi:application"

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn"]
'''

    print("\n🐳 EXEMPLO DE DOCKERFILE:")
    print(docker_example)


def show_kubernetes_example():
    """Mostrar exemplo de Kubernetes"""
    k8s_example = '''
# ConfigMap para Kubernetes
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
  
  # Configurações do Gunicorn
  GUNICORN_WORKERS: "4"
  GUNICORN_THREADS: "2"
  GUNICORN_TIMEOUT: "30"
  GUNICORN_MAX_REQUESTS: "1000"
  GUNICORN_LOG_LEVEL: "info"
'''

    print("\n☸️ EXEMPLO DE KUBERNETES CONFIGMAP:")
    print(k8s_example)


def main():
    """Função principal"""
    print("=" * 60)
    print("🧪 EXEMPLO DE INTEGRAÇÃO GUNICORN + DJANGO-CORALOGIX-OTEL")
    print("=" * 60)
    
    # Configurar ambiente
    setup_environment()
    
    # Verificar arquivos
    print("\n📁 VERIFICANDO ARQUIVOS:")
    gunicorn_ok = check_gunicorn_config()
    entrypoint_ok = check_entrypoint_script()
    
    if not gunicorn_ok or not entrypoint_ok:
        print("\n❌ Arquivos necessários não encontrados")
        return
    
    # Testar configuração
    config_ok = test_gunicorn_config()
    
    if config_ok:
        print("\n✅ TODOS OS TESTES PASSARAM!")
        
        # Gerar arquivo WSGI de exemplo
        generate_sample_wsgi()
        
        # Mostrar exemplos de uso
        show_usage_examples()
        show_docker_example()
        show_kubernetes_example()
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Configure CORALOGIX_PRIVATE_KEY com sua chave real")
        print("2. Ajuste myproject.wsgi:application para seu projeto")
        print("3. Execute: ./entrypoint.sh gunicorn")
        print("4. Verifique os logs para confirmar que OpenTelemetry está funcionando")
        
    else:
        print("\n❌ Alguns testes falharam. Verifique a configuração.")


if __name__ == "__main__":
    main()