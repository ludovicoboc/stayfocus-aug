# Configuração Inicial do Projeto Supabase

## Contexto

O StayFocus está em processo de migração de uma aplicação com armazenamento local para uma plataforma completa com backend robusto. O Supabase foi escolhido como solução de Backend-as-a-Service (BaaS) por oferecer um conjunto completo de ferramentas que atendem às necessidades do projeto, incluindo banco de dados PostgreSQL, autenticação, armazenamento de arquivos e sincronização em tempo real.

## Projeto Existente no Supabase

Atualmente, já existe um projeto Supabase criado para o StayFocus com as seguintes características:
- **Nome do Projeto**: StayFocus
- **ID do Projeto**: ngonttcfpjolvcszxgxk
- **Região**: sa-east-1 (América do Sul)
- **Status**: ACTIVE_HEALTHY
- **Versão do PostgreSQL**: 15.8.1.092

## Etapas de Configuração Inicial

### 1. Acesso ao Management Console Panel (MCP)

Para acessar o painel de administração do Supabase, utilize o seguinte URL:
```
https://app.supabase.com/project/ngonttcfpjolvcszxgxk
```

O MCP oferece uma interface gráfica para gerenciar todos os aspectos do projeto, incluindo:
- Banco de dados (tabelas, consultas, políticas)
- Autenticação e usuários
- Storage (armazenamento de arquivos)
- Edge Functions (funções serverless)
- Configurações de projeto

### 2. Configuração das Variáveis de Ambiente

Para integrar o Supabase ao projeto StayFocus, é necessário configurar as variáveis de ambiente. Crie um arquivo `.env` na raiz do projeto baseado no modelo `fastapi-backend/example.env`:

```bash
# Configurações do Banco de Dados
DATABASE_URL=postgresql://postgres:[SEU_PASSWORD]@db.ngonttcfpjolvcszxgxk.supabase.co:5432/postgres

# Configurações de Autenticação
SECRET_KEY=[GERAR_UMA_CHAVE_SECRETA_FORTE]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configurações do Supabase
SUPABASE_URL=https://ngonttcfpjolvcszxgxk.supabase.co
SUPABASE_KEY=[SUA_CHAVE_ANON_KEY]

# Configurações de E-mail (opcional)
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=[SUA_SENHA_SMTP]
EMAIL_FROM=noreply@stayfocus.app
```

Para obter as credenciais do Supabase:
1. Acesse o painel do projeto no Supabase
2. Navegue até "Settings" > "API"
3. Copie a "URL" e a "anon key" (chave pública)
4. Para o DATABASE_URL, use as credenciais de "Connection Pooling" em "Settings" > "Database"

### 3. Configuração do Cliente Supabase no Frontend

Crie a estrutura de diretórios para o cliente Supabase:

```bash
mkdir -p app/lib/supabase
```

Crie o arquivo de configuração do cliente Supabase:

```javascript
// app/lib/supabase/client.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Faltam variáveis de ambiente do Supabase. Verifique o arquivo .env.local')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### 4. Configuração do Cliente Supabase no Backend FastAPI

Crie um serviço para o Supabase no backend FastAPI:

```python
# fastapi-backend/app/services/supabase_service.py
from supabase import create_client, Client
from app.config import settings

def get_supabase_client() -> Client:
    """
    Cria e retorna um cliente Supabase configurado.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("Faltam variáveis de ambiente do Supabase. Verifique o arquivo .env")
    
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Cliente Supabase global para reutilização
supabase_client = get_supabase_client()
```

### 5. Verificação da Conexão

Para verificar se a conexão com o Supabase está funcionando corretamente, crie um endpoint de teste no FastAPI:

```python
# fastapi-backend/app/api/v1/endpoints/supabase.py
from fastapi import APIRouter, HTTPException, Depends
from app.services.supabase_service import get_supabase_client, supabase_client

router = APIRouter()

@router.get("/test-connection")
async def test_supabase_connection():
    """Testa a conexão com o Supabase"""
    try:
        # Tenta fazer uma consulta simples
        response = supabase_client.table('user_profiles').select('*').limit(1).execute()
        return {"status": "success", "message": "Conexão com Supabase estabelecida com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar com Supabase: {str(e)}")
```

## Próximos Passos

Após a configuração inicial do projeto Supabase, os próximos passos são:

1. Implementar o esquema de banco de dados conforme definido na documentação
2. Configurar as políticas de Row Level Security (RLS) para cada tabela
3. Implementar o sistema de autenticação
4. Configurar o armazenamento de arquivos (Storage)
5. Desenvolver as Edge Functions necessárias

A configuração inicial estabelece a base para todas as etapas subsequentes do projeto, garantindo que a comunicação entre o frontend, o backend FastAPI e o Supabase ocorra de forma segura e eficiente.
