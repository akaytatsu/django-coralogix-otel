"""
Django management command to check OpenTelemetry health.
"""

import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Check OpenTelemetry integration health"

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed health check information",
        )

    def handle(self, *args, **options):
        """Execute the health check command."""
        self.stdout.write(self.style.SUCCESS("🔍 OpenTelemetry Health Check"))
        self.stdout.write("=" * 50)

        # Check traces
        traces_ok = self._check_traces(options["verbose"])

        # Check metrics
        metrics_ok = self._check_metrics(options["verbose"])

        # Check logging
        logging_ok = self._check_logging(options["verbose"])

        # Summary
        self.stdout.write("\n📊 RESUMO:")
        self.stdout.write(f'  Traces:    {"✅ OK" if traces_ok else "❌ FALHA"}')
        self.stdout.write(f'  Metrics:   {"✅ OK" if metrics_ok else "❌ FALHA"}')
        self.stdout.write(f'  Logging:   {"✅ OK" if logging_ok else "❌ FALHA"}')

        if all([traces_ok, metrics_ok, logging_ok]):
            self.stdout.write(self.style.SUCCESS("\n🎉 OpenTelemetry está funcionando corretamente!"))
        else:
            self.stdout.write(self.style.ERROR("\n⚠️ OpenTelemetry apresenta problemas. Verifique os logs acima."))

    def _check_traces(self, verbose):
        """Check if traces are working."""
        try:
            from opentelemetry import trace

            tracer = trace.get_tracer("health-check")

            with tracer.start_as_current_span("health-check") as span:
                span.set_attribute("health.check", "success")
                span.set_attribute("component", "django-coralogix-otel")

                # Get span context
                span_ctx = span.get_span_context()
                if span_ctx and span_ctx.is_valid:
                    if verbose:
                        self.stdout.write(f'  ✅ Trace ID: {format(span_ctx.trace_id, "032x")}')
                        self.stdout.write(f'  ✅ Span ID:  {format(span_ctx.span_id, "016x")}')
                    return True
                else:
                    self.stdout.write("  ❌ Span context inválido")
                    return False

        except Exception as e:
            self.stdout.write(f"  ❌ Erro traces: {e}")
            return False

    def _check_metrics(self, verbose):
        """Check if metrics are working."""
        try:
            from opentelemetry import metrics

            meter = metrics.get_meter("health-check")
            counter = meter.create_counter("health.check.counter")
            counter.add(1, {"status": "ok", "component": "django-coralogix-otel"})

            if verbose:
                self.stdout.write("  ✅ Métricas criadas e incrementadas")
            return True

        except Exception as e:
            self.stdout.write(f"  ❌ Erro métricas: {e}")
            return False

    def _check_logging(self, verbose):
        """Check if JSON logging is working."""
        try:
            # Test JSON formatter
            from django_coralogix_otel.simple_logging import JSONFormatterWithTrace

            formatter = JSONFormatterWithTrace()

            # Create test log record
            import logging

            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=1,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            # Format the record
            formatted = formatter.format(record)

            # Check if it's valid JSON
            import json

            json.loads(formatted)

            if verbose:
                self.stdout.write("  ✅ JSON formatter funcionando")
                self.stdout.write(f"  ✅ Formato: {formatted[:100]}...")
            return True

        except Exception as e:
            self.stdout.write(f"  ❌ Erro logging: {e}")
            return False
