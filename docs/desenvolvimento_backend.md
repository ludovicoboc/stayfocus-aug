# Documentação do Desenvolvimento do Backend - StayFocus

## Visão Geral
Este documento descreve as decisões técnicas, implementações realizadas e próximos passos para o desenvolvimento do backend do StayFocus, uma aplicação de gerenciamento de foco e produtividade.

## Decisões Técnicas

### 1. Stack Tecnológica
- **Framework**: FastAPI
  - **Motivo**: Alta performance, suporte nativo a async/await, geração automática de documentação OpenAPI e validação de dados integrada.
  - **Vantagens**: 
    - Desenvolvimento rápido de APIs
    - Suporte a WebSockets (útil para notificações em tempo real)
    - Documentação interativa automática

- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
  - **Motivo**: Suporte a relacionamentos complexos e consultas SQL avançadas.
  - **ORM**: SQLAlchemy
    - **Vantagens**:
      - Abstração do banco de dados
      - Suporte a migrações com Alembic
      - Tipagem forte com SQLModel (opcional)

### 2. Estrutura do Projeto
```
fastapi-backend/
├── app/
│   ├── api/           # Rotas da API
│   ├── models/        # Modelos do banco de dados
│   ├── schemas/       # Esquemas Pydantic
│   ├── auth/          # Autenticação e autorização
│   ├── database.py    # Configuração do banco
│   └── config.py      # Configurações da aplicação
├── migrations/        # Migrações do banco
├── tests/             # Testes automatizados
└── requirements.txt   # Dependências
```

### 3. Autenticação e Autorização
- **JWT (JSON Web Tokens)**
  - **Implementação**: Endpoints para login/registro
  - **Segurança**: Senhas hasheadas com bcrypt
  - **Refresh Tokens**: Para renovação automática de sessões

## Implementações Realizadas

### 1. Configuração Inicial
- [x] Configuração do ambiente de desenvolvimento
- [x] Estrutura básica do projeto
- [x] Configuração do SQLAlchemy e Alembic
- [x] Variáveis de ambiente com python-dotenv

### 2. Modelos de Dados
- [x] `User`: Gerenciamento de usuários
- [x] `UserPreferences`: Preferências do usuário
- [x] `DailyGoals`: Metas diárias
- [x] `Task`: Tarefas principais
- [x] `Subtask`: Subtarefas
- [x] `TimeEntry`: Registros de tempo

### 3. Autenticação
- [x] Sistema de autenticação JWT
- [x] Middleware de autenticação
- [x] Proteção de rotas

### 4. Endpoints Implementados
- [x] Autenticação (login/registro)
- [x] CRUD de usuários
- [x] CRUD de tarefas e subtarefas
- [x] Gerenciamento de tempo

## Próximas Etapas

### 1. Testes (Alta Prioridade)
- [ ] Testes unitários para modelos
- [ ] Testes de integração para endpoints
- [ ] Testes de autenticação
- [ ] Testes de desempenho

### 2. Aprimoramentos de Segurança
- [ ] Rate limiting
- [ ] CORS configurado corretamente
- [ ] Headers de segurança (CSP, HSTS, etc.)
- [ ] Validação de entrada mais rigorosa

### 3. Recursos Adicionais
- [ ] Upload de arquivos (imagens para tarefas)
- [ ] Exportação de dados (PDF/Excel)
- [ ] Integração com calendário (Google Calendar, etc.)
- [ ] Notificações em tempo real (WebSockets)

### 4. Documentação
- [ ] Documentação da API (OpenAPI/Swagger)
- [ ] Guia de contribuição
- [ ] Documentação de deploy

### 5. DevOps
- [ ] Dockerfile otimizado
- [ ] CI/CD pipeline
- [ ] Monitoramento (Prometheus/Grafana)
- [ ] Logging estruturado

## Como Contribuir

1. Clone o repositório
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure as variáveis de ambiente:
   ```bash
   cp example.env .env
   # Edite o .env conforme necessário
   ```
5. Execute as migrações:
   ```bash
   alembic upgrade head
   ```
6. Inicie o servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

## Considerações Finais

Esta documentação serve como um guia para o desenvolvimento contínuo do backend do StayFocus. À medida que o projeto evolui, este documento deve ser atualizado para refletir as mudanças na arquitetura e nas decisões técnicas.

Para quaisquer dúvidas ou sugestões, por favor, abra uma issue no repositório do projeto.
