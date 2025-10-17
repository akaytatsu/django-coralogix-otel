from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="django-coralogix-otel",
    version="1.0.61",
    author="Thiago Freitas",
    author_email="thiagosistemas3@gmail.com",
    description="Pacote Django para integração simplificada de OpenTelemetry com Coralogix",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akaytatsu/django-coralogix-otel",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest",
            "pytest-django",
            "black",
            "flake8",
            "isort",
        ],
    },
    scripts=[
        "scripts/entrypoint.sh",
        "scripts/setup_gunicorn_config.sh",
    ],
    include_package_data=True,
    data_files=[
        ("", ["gunicorn.config.py"]),
    ],
    zip_safe=False,
)
