SHELL:=/bin/bash
ARGS = $(filter-out $@,$(MAKECMDGOALS))
MAKEFLAGS += --silent
BASE_PATH=${PWD}
PYTHON_EXEC=python
VENV_PATH=~/venv/django-coralogix-otel

.PHONY: help install install-dev test lint format clean build publish

# Variáveis
PACKAGE_NAME=django-coralogix-otel

help: ## Exibe ajuda com todos os comandos disponíveis
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala o pacote em modo edição
	pip install -e .

install-dev: ## Instala dependências de desenvolvimento
	pip install -e .[dev]

setup-dev: ## Setup completo do ambiente de desenvolvimento
	./setup_dev.sh

test: ## Executa todos os testes
	pytest

test-verbose: ## Executa testes em modo verbose
	pytest -v

test-cov: ## Executa testes com cobertura
	pytest --cov=django_coralogix_otel --cov-report=html --cov-report=term

test-watch: ## Executa testes automaticamente ao alterar arquivos
	ptw --clear --

_lint: ## Verifica código com flake8
	flake8 .

_format: ## Formata código com black e isort
	black .
	isort .

format: _format _lint ## Formata e verifica código

format-check: ## Verifica se código está formatado (sem alterar)
	black . --check
	isort . --check-only

check-code: lint format-check ## Executa todas as verificações de código

quality: format lint test ## Executa formatação, lint e testes

clean: ## Limpa arquivos temporários
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf *.xml

build: ## Build do pacote para distribuição
	python -m build

publish-test: ## Publica versão de teste no PyPI
	python -m twine upload --repository testpypi dist/*

publish: ## Publica versão no PyPI
	python -m twine upload dist/*

install-local: build ## Instala pacote localmente após build
	pip install dist/*.whl

# Comandos Django (para testes com example_settings)
shell: ## Abre shell Django com settings de exemplo
	DJANGO_SETTINGS_MODULE=example_settings ${PYTHON_EXEC} -c "import django; django.setup(); import django.core.management; django.core.management.execute_from_command_line(['manage.py', 'shell'])"

check-imports: ## Verifica imports organizados
	isort . --diff

check-format: ## Verifica formatação sem alterar
	black . --diff --color

# Comandos de verificação específicos
flake8-check: ## Verifica apenas flake8
	@echo "Verificando flake8..."
	flake8 . --show-source

pre-commit: format lint test ## Executa verificações de pre-commit
	@echo "✅ Pre-commit checks passaram!"

# Versão e release
version: ## Mostra versão atual
	@python -c "import ${PACKAGE_NAME}; print(${PACKAGE_NAME}.__version__)"

bump-patch: ## Incrementa versão patch (0.0.1 -> 0.0.2)
	bump2version patch

bump-minor: ## Incrementa versão minor (0.1.0 -> 0.2.0)
	bump2version minor

bump-major: ## Incrementa versão major (1.0.0 -> 2.0.0)
	bump2version major

release-patch: bump-patch build publish ## Release patch version
	@echo "🚀 Versão patch publicada!"

release-minor: bump-minor build publish ## Release minor version
	@echo "🚀 Versão minor publicada!"

release-major: bump-major build publish ## Release major version
	@echo "🚀 Versão major publicada!"

# Documentação
docs-serve: ## Serve documentação localmente
	cd docs && make livehtml

# Ambiente virtual
create-venv: ## Cria ambiente virtual
	python3 -m venv ${VENV_PATH}
	${VENV_PATH}/bin/python -m pip install --upgrade pip setuptools wheel
	${VENV_PATH}/bin/pip install -e .[dev]

activate-venv: ## Mostra comando para ativar venv
	@echo "Execute: source ${VENV_PATH}/bin/activate"

# Verificação de segurança
security-check: ## Verifica vulnerabilidades de segurança
	safety check
	bandit -r django_coralogix_otel/

# Benchmark de performance
benchmark: ## Executa benchmarks (se disponível)
	@echo "Executando benchmarks..."
	@echo "Nenhum benchmark configurado ainda"

# Limpeza completa
deep-clean: clean ## Limpeza completa incluindo venv
	rm -rf ${VENV_PATH}
	rm -rf .tox/
	rm -rf .mypy_cache/