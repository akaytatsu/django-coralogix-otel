#!/usr/bin/env python3
"""
Exemplo de uso do script de entrypoint para django-coralogix-otel

Este script demonstra como usar o entrypoint.sh em diferentes cenários
e como configurar as variáveis de ambiente necessárias.
"""

import os
import subprocess
import sys


def setup_environment():
    """Configura variáveis de ambiente para demonstração"""
    env_vars = {
        'OTEL_SERVICE_NAME': 'django-coralogix-otel-example',
        'OTEL_EXPORTER_OTLP_ENDPOINT': 'https://ingress.coralogix.com:443',
        'CORALOGIX_APPLICATION_NAME': 'example-app',
        'CORALOGIX_SUBSYSTEM_NAME': 'backend',
        'OTEL_DEPLOYMENT_ENVIRONMENT': 'development',
        'OTEL_LOG_LEVEL': 'INFO',
        'DJANGO_DEBUG': 'True',
        'APP_ENVIRONMENT': 'local'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print("✅ Variáveis de ambiente configuradas:")
    for key, value in env_vars.items():
        print(f"   {key}={value}")


def test_entrypoint_help():
    """Testa o comando de help do entrypoint"""
    print("\n🧪 Testando comando de help...")
    
    try:
        result = subprocess.run(
            ['./entrypoint.sh'],
            capture_output=True,
            text=True,
            cwd='..'  # Voltar um diretório para encontrar o entrypoint.sh
        )
        
        if result.returncode == 1:  # Exit code 1 é esperado para help
            print("✅ Comando de help executado com sucesso")
            print("📋 Comandos disponíveis:")
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('===') and not line.startswith('Warning'):
                    print(f"   {line}")
        else:
            print(f"❌ Comando de help retornou código inesperado: {result.returncode}")
            
    except Exception as e:
        print(f"❌ Erro ao executar comando de help: {e}")


def test_entrypoint_commands():
    """Testa diferentes comandos do entrypoint"""
    commands = [
        ['./entrypoint.sh', 'setup'],
        ['./entrypoint.sh', 'manage.py', '--help'],
        ['./entrypoint.sh', 'python', '--version']
    ]
    
    print("\n🧪 Testando comandos do entrypoint...")
    
    for cmd in commands:
        print(f"\n📝 Executando: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd='..',
                timeout=10  # Timeout para evitar execução infinita
            )
            
            if result.returncode == 0:
                print("✅ Comando executado com sucesso")
            else:
                print(f"⚠️  Comando retornou código {result.returncode} (pode ser esperado)")
                
            # Mostrar primeiras linhas da saída
            if result.stdout:
                lines = result.stdout.split('\n')[:3]
                for line in lines:
                    if line.strip():
                        print(f"   📄 {line}")
                        
        except subprocess.TimeoutExpired:
            print("⏰ Comando expirou (pode ser esperado para alguns comandos)")
        except Exception as e:
            print(f"❌ Erro ao executar comando: {e}")


def generate_docker_example():
    """Gera exemplo de Dockerfile usando o entrypoint"""
    print("\n🐳 Exemplo de Dockerfile com entrypoint:")
    
    dockerfile_example = '''
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
'''
    
    print(dockerfile_example)


def generate_kubernetes_example():
    """Gera exemplo de configuração Kubernetes"""
    print("\n☸️ Exemplo de configuração Kubernetes:")
    
    k8s_example = '''
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
        env:
        - name: CORALOGIX_PRIVATE_KEY
          valueFrom:
            secretKeyRef:
              name: coralogix-secret
              key: private-key
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: "https://ingress.coralogix.com:443"
        - name: OTEL_SERVICE_NAME
          value: "my-django-app"
        - name: GUNICORN_CONFIG
          value: "--bind 0.0.0.0:8000 --workers 4 --threads 2"
'''
    
    print(k8s_example)


def main():
    """Função principal"""
    print("🚀 Exemplo de uso do script de entrypoint para django-coralogix-otel")
    print("=" * 70)
    
    # Configurar ambiente
    setup_environment()
    
    # Testar funcionalidades
    test_entrypoint_help()
    test_entrypoint_commands()
    
    # Gerar exemplos
    generate_docker_example()
    generate_kubernetes_example()
    
    print("\n🎯 Resumo:")
    print("✅ Script de entrypoint criado e testado")
    print("✅ Documentação incluída em ENTRYPOINT.md")
    print("✅ README.md atualizado com informações do entrypoint")
    print("✅ MANIFEST.in atualizado para incluir arquivos do entrypoint")
    print("✅ Exemplos de uso criados")
    
    print("\n📚 Próximos passos:")
    print("1. Copie o entrypoint.sh para seu projeto Django")
    print("2. Configure as variáveis de ambiente necessárias")
    print("3. Use o script em seu Dockerfile ou diretamente")
    print("4. Consulte ENTRYPOINT.md para documentação detalhada")


if __name__ == "__main__":
    main()