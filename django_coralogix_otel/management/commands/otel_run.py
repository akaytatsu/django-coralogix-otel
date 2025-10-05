"""
Management command to run Django with OpenTelemetry instrumentation.
"""

import os
import sys

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run Django command with OpenTelemetry instrumentation"

    def add_arguments(self, parser):
        parser.add_argument("command_args", nargs="*", help="Arguments to pass to the Django command")

    def handle(self, *args, **options):
        """Execute the command with OpenTelemetry instrumentation."""

        # Set up OpenTelemetry environment variables
        os.environ.setdefault("OTEL_PYTHON_INSTRUMENTATION_ENABLED", "true")
        os.environ.setdefault("OTEL_PYTHON_DJANGO_INSTRUMENT", "true")
        os.environ.setdefault("OTEL_PYTHON_REQUESTS_INSTRUMENT", "true")
        os.environ.setdefault("OTEL_PYTHON_PSYCOPG2_INSTRUMENT", "true")
        os.environ.setdefault("OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED", "true")

        # Get command arguments
        command_args = options.get("command_args", [])

        if not command_args:
            self.stdout.write(self.style.ERROR("No command specified. Usage: manage.py otel_run <command> [args]"))
            return

        # Re-execute the current script with opentelemetry-instrument
        import subprocess

        cmd = ["opentelemetry-instrument", "python", "manage.py"] + command_args

        self.stdout.write(self.style.SUCCESS(f'Executing: {" ".join(cmd)}'))

        # Execute the command
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
