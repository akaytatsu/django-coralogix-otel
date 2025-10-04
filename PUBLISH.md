# Django Coralogix OpenTelemetry - Guia de Publicação

## 📦 Passos para Publicar no PyPI

### 1. Preparação
```bash
# Instalar dependências de build
pip install build twine

# Testar o pacote localmente
pip install -e .
python -c "import django_coralogix_otel; print(django_coralogix_otel.__version__)"
```

### 2. Build do Pacote
```bash
# Limpar builds anteriores
rm -rf dist/ build/ *.egg-info/

# Build do pacote
python -m build
```

### 3. Testar no TestPyPI
```bash
# Upload para testes
twine upload --repository testpypi dist/*

# Instalar do TestPyPI
pip install --index-url https://test.pypi.org/simple/ django-coralogix-otel
```

### 4. Publicar no PyPI
```bash
# Upload para produção
twine upload dist/*
```

## 🏗️ Estrutura Final

O pacote está pronto com:
- ✅ Configuração automática via Django AppConfig
- ✅ Logging estruturado com trace context
- ✅ Middleware para enriquecimento de traces
- ✅ Management commands para facilitar uso
- ✅ Script de inicialização bash
- ✅ Configuração flexível via settings
- ✅ Documentação completa
- ✅ Exemplos de uso
- ✅ Setup para PyPI (pyproject.toml + setup.py)

## 🚀 Uso Básico

### Instalação:
```bash
pip install django-coralogix-otel
```

### Configuração:
```python
# settings.py
INSTALLED_APPS = [
    'django_coralogix_otel',
    # ...
]

from django_coralogix_otel.logging_config import LOGGING_CONFIG
LOGGING = LOGGING_CONFIG
```

### Variáveis de Ambiente:
```bash
export OTEL_SERVICE_NAME=meu-servico
export OTEL_EXPORTER_OTLP_ENDPOINT=https://ingress.coralogix.com:443
export OTEL_EXPORTER_OTLP_HEADERS=Authorization=Bearer YOUR_API_KEY
```

O pacote está pronto para publicação e uso em múltiplos projetos Django!