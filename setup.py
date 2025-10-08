#!/usr/bin/env python
"""
Setup script para django-coralogix-otel
"""

import os

from setuptools import find_packages, setup

# Ler o conteúdo do README para a descrição longa
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Ler a versão do pacote
with open("django_coralogix_otel/__init__.py", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break
    else:
        version = "0.1.0"

setup(
    name="django-coralogix-otel",
    version=version,
    author="Thiago Freitas",
    author_email="thiagosistemas3@gmail.com",
    description="Auto-instrumentação OpenTelemetry com Coralogix para aplicações Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vertc-developers/django-coralogix-otel",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Topic :: System :: Monitoring",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        # OpenTelemetry Core
        "opentelemetry-api>=1.20.0",
        "opentelemetry-sdk>=1.20.0",
        "opentelemetry-distro[otlp]>=0.41.0",
        # OpenTelemetry Instrumentation
        "opentelemetry-instrumentation>=0.41.0",
        "opentelemetry-instrumentation-django>=0.41.0",
        "opentelemetry-instrumentation-psycopg2>=0.41.0",
        "opentelemetry-instrumentation-requests>=0.41.0",
        "opentelemetry-instrumentation-logging>=0.41.0",
        "opentelemetry-instrumentation-wsgi>=0.41.0",
        "opentelemetry-instrumentation-asgi>=0.41.0",
        # OpenTelemetry Exporters
        "opentelemetry-exporter-otlp-proto-http>=1.20.0",
        # Django
        "Django>=3.2",
        # Dependências opcionais (instaladas apenas se necessárias)
        "opentelemetry-instrumentation-kafka-python>=0.41.0; extra == 'kafka'",
    ],
    extras_require={
        "kafka": ["opentelemetry-instrumentation-kafka-python>=0.41.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-django>=4.5.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.910",
            "isort>=5.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "django-coralogix-init=django_coralogix_otel.entrypoint:initialize_opentelemetry",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "django",
        "opentelemetry",
        "coralogix",
        "observability",
        "monitoring",
        "tracing",
        "metrics",
        "logging",
    ],
    project_urls={
        "Bug Reports": "https://github.com/vertc-developers/django-coralogix-otel/issues",
        "Source": "https://github.com/vertc-developers/django-coralogix-otel",
    },
)
