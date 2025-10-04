# Django Coralogix OpenTelemetry - Guia de Desenvolvimento

## ⚠️ IMPORTANTE: COMUNICAÇÃO EM PORTUGUÊS BRASIL
**TODA comunicação com agentes de IA deve ser exclusivamente em PORTUGUÊS DO BRASIL.** Não responda em inglês ou outros idiomas.

## 🛠️ Comandos de Desenvolvimento

### Instalação e Setup
```bash
# Usando Makefile (recomendado)
make install-dev        # Instala dependências de desenvolvimento
make setup-dev          # Setup completo do ambiente
make create-venv        # Cria ambiente virtual

# Manualmente
pip install -e .[dev]
./setup_dev.sh

# Build do pacote
make build
python -m build
```

### Testes
```bash
# Usando Makefile (recomendado)
make test               # Executar todos os testes
make test-verbose       # Executar em modo verbose
make test-cov           # Executar com cobertura HTML
make test-watch         # Executar automaticamente ao alterar arquivos

# Manualmente
pytest
pytest tests/test_file.py::test_function_name
pytest --cov=django_coralogix_otel
pytest -v
```

### Lint e Formatação
```bash
# Usando Makefile (recomendado)
make format             # Formatar código (black + isort)
make lint               # Verificar código (flake8)
make check-code         # Verificar formatação e lint
make quality            # Executar tudo (format + lint + test)
make pre-commit         # Verificações completas de pre-commit

# Manualmente
black .
isort .
flake8 .
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
- Usar `black` para formatação automática (linha máxima 120 caracteres)
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

## 🚀 Comandos Úteis do Makefile

```bash
# Ajuda
make help              # Mostra todos os comandos disponíveis

# Publicação
make publish           # Publicar no PyPI
make publish-test      # Publicar no PyPI de teste
make release-patch     # Release automático de versão patch

# Limpeza
make clean             # Limpa arquivos temporários
make deep-clean        # Limpeza completa incluindo venv

# Segurança
make security-check    # Verifica vulnerabilidades

# Versão
make version           # Mostra versão atual
```