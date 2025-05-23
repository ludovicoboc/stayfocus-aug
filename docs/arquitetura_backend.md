# Arquitetura do Backend - StayFocus

## Visão Geral da Arquitetura

O backend do StayFocus foi projetado seguindo os princípios de Arquitetura Limpa (Clean Architecture) e padrões de design modernos para garantir escalabilidade, manutenibilidade e segurança. Este documento detalha as decisões técnicas e a estrutura do projeto.

## 1. Estrutura do Projeto

```
fastapi-backend/
├── app/
│   ├── api/               # Camada de API
│   │   └── v1/            # Versão 1 da API
│   │       ├── endpoints/  # Rotas da API
│   │       └── deps.py    # Dependências (autenticação, etc.)
│   │
│   ├── core/             # Configurações e serviços centrais
│   │   ├── config.py      # Configurações da aplicação
│   │   ├── security.py    # Autenticação e autorização
│   │   └── supabase.py    # Cliente Supabase
│   │
│   ├── models/          # Modelos SQLAlchemy
│   ├── schemas/          # Esquemas Pydantic
│   ├── services/         # Lógica de negócio
│   └── utils/            # Utilitários
├── migrations/           # Migrações do banco
└── tests/               # Testes automatizados
```

## 2. Decisões Técnicas

### 2.1 Framework e Bibliotecas Principais

- **FastAPI**: Framework web moderno e rápido (baseado em Starlette) para construção de APIs
- **SQLAlchemy**: ORM para interação com o banco de dados
- **Pydantic**: Validação de dados e gerenciamento de esquemas
- **Supabase**: Backend como serviço para autenticação e banco de dados
- **Alembic**: Para migrações de banco de dados

### 2.2 Padrões de Projeto

- **Repository Pattern**: Para abstrair o acesso a dados
- **Dependency Injection**: Para injeção de dependências
- **Factory Pattern**: Para criação de objetos complexos
- **Strategy Pattern**: Para implementação de diferentes estratégias de autenticação

## 3. Autenticação e Autorização

### 3.1 Fluxo de Autenticação

1. Cliente envia credenciais para `/api/v1/auth/token`
2. Servidor valida as credenciais no Supabase Auth
3. Se válido, gera um JWT e retorna para o cliente
4. Cliente envia o token no header `Authorization: Bearer <token>`
5. Middleware valida o token em cada requisição

### 3.2 Políticas de Segurança

- **JWT com tempo de expiração curto**
- **Refresh tokens** para renovação de sessão
- **HTTPS** obrigatório em produção
- **CORS** configurado de forma restritiva
- **Rate limiting** para prevenir abusos

## 4. Integração com Supabase

### 4.1 Configuração do Cliente

```python
# app/core/supabase.py
from supabase import create_client, Client
from app.core.config import settings

supabase: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY
)
```

### 4.2 Autenticação

```python
# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
```

## 5. Gerenciamento de Dados

### 5.1 Modelos SQLAlchemy

```python
# app/models/task.py
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base, TimestampMixin

class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending")
    priority = Column(Integer, default=2)  # 1: Baixa, 2: Média, 3: Alta
    is_important = Column(Boolean, default=False)
    is_urgent = Column(Boolean, default=False)
```

### 5.2 Esquemas Pydantic

```python
# app/schemas/task.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    priority: Optional[int] = 2
    is_important: Optional[bool] = False
    is_urgent: Optional[bool] = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    is_important: Optional[bool] = None
    is_urgent: Optional[bool] = None

class TaskInDB(TaskBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

## 6. Endpoints da API

### 6.1 Exemplo de Rota

```python
# app/api/v1/endpoints/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.TaskInDB])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Lista todas as tarefas do usuário"""
    tasks = db.query(models.Task).filter(
        models.Task.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return tasks
```

## 7. Próximos Passos

### 7.1 Melhorias de Desempenho

- [ ] Implementar cache com Redis
- [ ] Otimizar consultas ao banco de dados
- [ ] Adicionar índices para campos de busca frequentes

### 7.2 Segurança

- [ ] Implementar rate limiting
- [ ] Adicionar validação de entrada mais rigorosa
- [ ] Configurar CORS de forma mais restritiva

### 7.3 Funcionalidades Futuras

- [ ] Upload de arquivos
- [ ] Notificações em tempo real
- [ ] Relatórios e análises

## 8. Considerações Finais

Esta arquitetura foi projetada para ser flexível e escalável, permitindo a adição de novos recursos com o mínimo de impacto no código existente. O uso de padrões de projeto bem estabelecidos e a separação clara de responsabilidades facilitam a manutenção e os testes do sistema.
