# Changelog

## [1.1.0] - 2025-10-08

### Fixed
- **Correção crítica**: Compatibilidade com `opentelemetry-instrument`
- Resolvido erro `settings.DATABASES is improperly configured` ao usar auto-instrumentação
- Implementada detecção automática de comandos Django sensíveis (migrate, showmigrations, etc.)
- Adicionado tratamento robusto de erros para evitar quebrar inicialização do Django

### Added
- `configure_opentelemetry_safe()` - versão segura que nunca levanta exceções
- Detecção inteligente de comandos management que podem ser afetados pelo OpenTelemetry
- Tratamento de erros no `JSONFormatterWithTrace` com fallback para JSON simples
- Script `django-coralogix-otel-run` melhorado com troubleshooting e ajuda
- Documentação completa de instalação e troubleshooting (`INSTALLATION.md`)

### Changed
- `apps.py`: Agora detecta e pula configuração para comandos sensíveis
- `otel_config.py`: Configuração mais segura com tratamento de exceções
- `logging_config.py`: Formatter mais robusto que não falha se trace context não estiver disponível
- Script wrapper: Melhor feedback e ajuda para debugging

### Security
- Melhor validação de ambiente para evitar expor informações sensíveis em logs de erro

### Compatibility
- **Totalmente compatível com `opentelemetry-instrument`**
- Funciona com todos os comandos Django management
- Suporte a Django 3.2, 4.x, 5.x
- Suporte a Python 3.8+

---

## [1.0.0] - 2025-10-07

### Added
- Configuração simplificada de OpenTelemetry para Django
- Integração com Coralogix via resource attributes
- Logging estruturado JSON com trace context
- Middleware para rastreamento automático de requisições
- Script wrapper para fácil uso em produção
- Suporte para PostgreSQL, Requests, WSGI, ASGI, Kafka