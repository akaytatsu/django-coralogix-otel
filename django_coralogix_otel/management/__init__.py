"""
Management commands Django para OpenTelemetry e Coralogix.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Verifica a configuração do OpenTelemetry e Coralogix'
    
    def handle(self, *args, **options):
        """Executa o comando de verificação."""
        self.stdout.write("=== Verificação do OpenTelemetry e Coralogix ===")
        
        # Importa as funções do pacote
        try:
            from django_coralogix_otel.config import configure_opentelemetry, get_resource
            from django_coralogix_otel.middleware import CoralogixMiddleware
            
            # Verifica variáveis de ambiente
            self._check_environment_variables()
            
            # Configura e verifica
            configure_opentelemetry()
            
            # Obtém resource
            resource = get_resource()
            self.stdout.write(self.style.SUCCESS(f"Resource configurado: {resource.attributes}"))
            
            # Verifica instrumentação
            self._check_instrumentation()
            
            self.stdout.write(self.style.SUCCESS("✅ OpenTelemetry e Coralogix configurados com sucesso!"))
            
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro de importação: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro na configuração: {e}"))
    
    def _check_environment_variables(self):
        """Verifica variáveis de ambiente configuradas."""
        import os
        
        required_vars = ["OTEL_SERVICE_NAME"]
        optional_vars = [
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "OTEL_RESOURCE_ATTRIBUTES",
            "OTEL_IP",
            "APP_ENVIRONMENT"
        ]
        
        self.stdout.write("\n📋 Variáveis de Ambiente:")
        
        # Verifica obrigatórias
        for var in required_vars:
            value = os.getenv(var)
            if value:
                self.stdout.write(f"  ✅ {var}: {value}")
            else:
                self.stdout.write(self.style.ERROR(f"  ❌ {var}: não definida"))
        
        # Verifica opcionais
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                self.stdout.write(f"  ✅ {var}: {value}")
            else:
                self.stdout.write(f"  ⚠️  {var}: não definida (opcional)")
    
    def _check_instrumentation(self):
        """Verifica se a instrumentação está ativa."""
        try:
            from opentelemetry.instrumentation.django import DjangoInstrumentor
            from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
            from opentelemetry.instrumentation.requests import RequestsInstrumentor
            from opentelemetry.instrumentation.logging import LoggingInstrumentor
            
            self.stdout.write("\n🔧 Instrumentação:")
            
            instrumentations = [
                ("Django", DjangoInstrumentor),
                ("PostgreSQL", Psycopg2Instrumentor),
                ("Requests", RequestsInstrumentor),
                ("Logging", LoggingInstrumentor),
            ]
            
            for name, instrumentor in instrumentations:
                try:
                    inst = instrumentor()
                    if inst.is_instrumented_by_opentelemetry:
                        self.stdout.write(f"  ✅ {name}: habilitado")
                    else:
                        self.stdout.write(f"  ⚠️  {name}: não habilitado")
                except Exception as e:
                    self.stdout.write(f"  ❌ {name}: erro - {e}")
                    
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f"❌ Não foi possível verificar instrumentação: {e}"))