# Django Coralogix OpenTelemetry - Guia de Desenvolvimento

## ⚠️ IMPORTANTE: COMUNICAÇÃO EM PORTUGUÊS BRASIL
**TODA comunicação com agentes de IA deve ser exclusivamente em PORTUGUÊS DO BRASIL.** Não responda em inglês ou outros idiomas.

## 🛠️ Comandos de Desenvolvimento

### Instalação e Setup
```bash
# Instalar em modo desenvolvimento
pip install -e .[dev]

# Setup rápido (cria venv e instala dependências)
./setup_dev.sh

# Build do pacote
python -m build
```

### Testes
```bash
# Executar todos os testes
pytest

# Executar teste específico
pytest tests/test_file.py::test_function_name

# Executar com cobertura
pytest --cov=django_coralogix_otel

# Executar em modo verbose
pytest -v
```

### Lint e Formatação
```bash
# Formatar código
black .
isort .

# Lint
flake8 .

# Executar tudo (lint + format + test)
black . && isort . && flake8 . && pytest
```

## 📋 Estilo de Código

### Imports e Estrutura
- Imports padrão Python primeiro, depois de terceiros, depois locais
- Usar `isort` para organizar imports automaticamente
- Imports relativos para módulos do mesmo pacote

### Nomenclatura
- Classes: `PascalCase` (ex: `TraceMiddleware`)
- Funções e variáveis: `snake_case` (ex: `setup_tracing`)
- Constantes: `UPPER_SNAKE_CASE` (ex: `LOGGING_CONFIG`)
- Privados: prefixo `_` (ex: `_get_config()`)

### Formatação
- Usar `black` para formatação automática (linha máxima 88 caracteres)
- `flake8` para linting (configuração padrão)
- Docstrings seguindo estilo Google ou Sphinx

### Tratamento de Erros
- Usar `try/except` específicos
- Log de erros com `logger.error()`
- Evitar `except Exception:` genérico
- Retornar valores padrão seguros em caso de erro

### Padrões Django
- Apps em `snake_case`
- Middleware seguindo padrão Django
- Configurações via `settings.py` com prefixo `DJANGO_CORALOGIX_OTEL`
- Use `getattr(settings, 'SETTING_NAME', default)` para valores opcionais

### OpenTelemetry
- Sempre verificar se instrumentação já está ativa
- Usar fallback para console exporters em desenvolvimento
- Incluir trace context em logs estruturados
- Resource attributes com prefixos adequados (cx.* para Coralogix)

### Logging
- Logs estruturados em JSON para produção
- Incluir trace_id e span_id quando disponível
- Níveis apropriados: ERROR para falhas, WARNING para problemas, INFO para geral
- Evitar logs sensíveis (senhas, tokens)