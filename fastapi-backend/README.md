# StayFocus API

Esta é uma API RESTful desenvolvida com FastAPI para o sistema StayFocus, um aplicativo de gerenciamento de foco e produtividade.

## 🚀 Começando

### Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes do Python)
- PostgreSQL (recomendado) ou SQLite

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/stayfocus-backend.git
   cd fastapi-backend
   ```

2. Crie e ative um ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: .\venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   ```bash
   cp example.env .env
   # Edite o arquivo .env com suas configurações
   ```

### Executando a aplicação

```bash
uvicorn app.main:app --reload
```

A API estará disponível em: http://127.0.0.1:8000

Documentação interativa (Swagger UI): http://127.0.0.1:8000/docs  
Documentação alternativa (ReDoc): http://127.0.0.1:8000/redoc

## 🛠️ Estrutura do Projeto

```
fastapi-backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # Ponto de entrada da aplicação
│   ├── api/             # Rotas da API (versão 1)
│   ├── models/          # Modelos do banco de dados
│   ├── schemas/         # Esquemas Pydantic para validação
│   ├── database.py      # Configuração do banco de dados
│   └── config.py        # Configurações da aplicação
├── tests/               # Testes automatizados
├── .env                 # Variáveis de ambiente (não versionado)
├── .gitignore
├── requirements.txt     # Dependências do projeto
└── README.md
```

## 🔐 Autenticação

A API utiliza autenticação JWT (JSON Web Tokens). Para autenticar suas requisições:

1. Faça login para obter um token:
   ```
   POST /api/v1/auth/token
   ```
   Corpo da requisição (form-data):
   ```
   username: seu@email.com
   password: sua_senha
   ```

2. Use o token nas requisições subsequentes:
   ```
   Authorization: Bearer seu_token_aqui
   ```

## 📚 Endpoints Principais

### Autenticação
- `POST /api/v1/auth/token` - Gera um token de acesso
- `POST /api/v1/auth/register` - Registra um novo usuário
- `GET /api/v1/auth/me` - Retorna os dados do usuário logado

### Usuários
- `GET /api/v1/users/me` - Retorna os dados do usuário atual
- `PUT /api/v1/users/me` - Atualiza os dados do usuário atual
- `GET /api/v1/users/me/preferences` - Retorna as preferências do usuário
- `PUT /api/v1/users/me/preferences` - Atualiza as preferências do usuário

### Tarefas
- `GET /api/v1/tasks/` - Lista todas as tarefas do usuário
- `POST /api/v1/tasks/` - Cria uma nova tarefa
- `GET /api/v1/tasks/{task_id}` - Obtém uma tarefa específica
- `PUT /api/v1/tasks/{task_id}` - Atualiza uma tarefa
- `DELETE /api/v1/tasks/{task_id}` - Remove uma tarefa

### Subtarefas
- `GET /api/v1/tasks/{task_id}/subtasks` - Lista as subtarefas de uma tarefa
- `POST /api/v1/tasks/{task_id}/subtasks` - Adiciona uma subtarefa

### Registros de Tempo
- `POST /api/v1/tasks/{task_id}/time-entries` - Registra tempo gasto em uma tarefa
- `GET /api/v1/tasks/time-entries/summary` - Resumo do tempo gasto

## 🧪 Testes

Para executar os testes:

```bash
pytest
```

## 🚀 Implantação

### Com Docker (Recomendado)

1. Construa a imagem:
   ```bash
   docker build -t stayfocus-api .
   ```

2. Execute o contêiner:
   ```bash
   docker run -d --name stayfocus-api -p 8000:8000 --env-file .env stayfocus-api
   ```

### Sem Docker

1. Instale as dependências de produção:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute com Gunicorn (produção):
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature (`git checkout -b feature/AmazingFeature`)
3. Adicione suas mudanças (`git add .`)
4. Comite suas mudanças (`git commit -m 'Add some AmazingFeature'`)
5. Faça o Push da Branch (`git push origin feature/AmazingFeature`)
6. Abra um Pull Request
│   └── services/        # Lógica de negócio
└── requirements.txt     # Dependências do projeto
```

## 📚 Endpoints

### Hiperfocos

- `GET /`: Rota inicial
- `POST /hiperfocos/`: Cria um novo hiperfoco
- `GET /hiperfocos/`: Lista todos os hiperfocos
- `GET /hiperfocos/{hiperfoco_id}`: Obtém um hiperfoco específico

## 🔄 Desenvolvimento

Para desenvolvimento, você pode usar o modo de recarga automática:

```bash
uvicorn app.main:app --reload
```

## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
