from django.core.management.base import BaseCommand
import os
import shutil


class Command(BaseCommand):
    help = "Copy gunicorn.config.py from django-coralogix-otel to project root"

    def handle(self, *args, **options):
        try:
            from django_coralogix_otel import get_gunicorn_config_path

            source_path = get_gunicorn_config_path()

            if not source_path:
                self.stdout.write(self.style.ERROR("gunicorn.config.py not found in django-coralogix-otel"))
                return

            dest_path = "gunicorn.config.py"

            # Copiar arquivo
            shutil.copy2(source_path, dest_path)

            self.stdout.write(self.style.SUCCESS(f"Successfully copied gunicorn.config.py to {dest_path}"))

        except ImportError:
            self.stdout.write(self.style.ERROR("django-coralogix-otel not installed"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error copying gunicorn.config.py: {e}"))
