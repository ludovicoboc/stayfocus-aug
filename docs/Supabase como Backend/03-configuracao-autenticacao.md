# Configuração de Autenticação

## Contexto

A autenticação é um componente crítico do StayFocus, permitindo que os usuários acessem seus dados de forma segura em diferentes dispositivos. O Supabase oferece um sistema de autenticação robusto e flexível, com suporte para diversos métodos de autenticação, incluindo email/senha, OAuth com provedores sociais, e autenticação sem senha (magic link).

A migração do sistema atual para o Supabase Auth requer uma implementação cuidadosa para garantir uma experiência de usuário fluida e manter a segurança dos dados.

## Métodos de Autenticação

Para o StayFocus, implementaremos os seguintes métodos de autenticação:

### 1. Email/Senha

Este é o método principal de autenticação, permitindo que os usuários criem contas com email e senha.

### 2. Google OAuth

Integração com Google OAuth para permitir login com contas Google, facilitando o acesso e melhorando a experiência do usuário.

## Configuração no Supabase MCP

### 1. Configuração de Email/Senha

1. Acesse o painel do Supabase e navegue até "Authentication" > "Providers"
2. Certifique-se de que o provedor "Email" esteja habilitado
3. Configure as opções de segurança:
   - Comprimento mínimo da senha: 8 caracteres
   - Exigir pelo menos uma letra maiúscula
   - Exigir pelo menos um número
4. Configure as opções de confirmação de email:
   - Habilitar confirmação de email
   - Personalizar o template de email de confirmação

### 2. Configuração do Google OAuth

1. Acesse o painel do Supabase e navegue até "Authentication" > "Providers"
2. Habilite o provedor "Google"
3. Configure as credenciais do Google OAuth:
   - Client ID: [SEU_GOOGLE_CLIENT_ID]
   - Client Secret: [SEU_GOOGLE_CLIENT_SECRET]
   - URL de redirecionamento: https://ngonttcfpjolvcszxgxk.supabase.co/auth/v1/callback

Para obter as credenciais do Google OAuth:
1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Navegue até "APIs & Services" > "Credentials"
4. Crie um novo "OAuth client ID" do tipo "Web application"
5. Adicione a URL de redirecionamento do Supabase

### 3. Configuração de Políticas de Segurança

1. Acesse o painel do Supabase e navegue até "Authentication" > "Policies"
2. Configure as políticas de segurança:
   - Duração da sessão: 7 dias
   - Duração do refresh token: 30 dias
   - Habilitar proteção contra força bruta
   - Configurar limites de taxa para tentativas de login

## Implementação no Frontend

### 1. Instalação das Dependências

```bash
npm install @supabase/supabase-js
```

### 2. Criação de Hooks de Autenticação

Crie um hook personalizado para gerenciar a autenticação:

```typescript
// app/hooks/useAuth.ts
import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase/client'
import { User, Session } from '@supabase/supabase-js'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Obter sessão atual
    const getSession = async () => {
      setLoading(true)
      const { data: { session }, error } = await supabase.auth.getSession()
      
      if (error) {
        console.error('Erro ao obter sessão:', error)
      }
      
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    }

    getSession()

    // Configurar listener para mudanças de autenticação
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session)
        setUser(session?.user ?? null)
        setLoading(false)
      }
    )

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  // Função para login com email/senha
  const signInWithEmail = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    
    return { data, error }
  }

  // Função para login com Google
  const signInWithGoogle = async () => {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin + '/auth/callback',
      },
    })
    
    return { data, error }
  }

  // Função para registro com email/senha
  const signUpWithEmail = async (email: string, password: string, userData: any) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: userData,
        emailRedirectTo: window.location.origin + '/auth/callback',
      },
    })
    
    return { data, error }
  }

  // Função para logout
  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    return { error }
  }

  return {
    user,
    session,
    loading,
    signInWithEmail,
    signInWithGoogle,
    signUpWithEmail,
    signOut,
  }
}
```

### 3. Criação de Componentes de Autenticação

Crie componentes para login, registro e gerenciamento de perfil:

```tsx
// app/components/auth/LoginForm.tsx
import { useState } from 'react'
import { useAuth } from '../../hooks/useAuth'

export function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const { signInWithEmail, signInWithGoogle } = useAuth()

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    const { error } = await signInWithEmail(email, password)
    
    if (error) {
      setError(error.message)
    }
    
    setLoading(false)
  }

  const handleGoogleLogin = async () => {
    setLoading(true)
    setError(null)
    
    const { error } = await signInWithGoogle()
    
    if (error) {
      setError(error.message)
    }
    
    setLoading(false)
  }

  return (
    <div className="auth-form">
      <h2>Login</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleEmailLogin}>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Senha</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Entrando...' : 'Entrar'}
        </button>
      </form>
      
      <div className="social-login">
        <button onClick={handleGoogleLogin} disabled={loading}>
          Entrar com Google
        </button>
      </div>
    </div>
  )
}
```

### 4. Configuração de Rotas Protegidas

Crie um componente para proteger rotas que requerem autenticação:

```tsx
// app/components/auth/ProtectedRoute.tsx
import { useRouter } from 'next/router'
import { useAuth } from '../../hooks/useAuth'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, loading } = useAuth()
  const router = useRouter()

  // Verificar se está carregando
  if (loading) {
    return <div>Carregando...</div>
  }

  // Redirecionar para login se não estiver autenticado
  if (!user) {
    router.push('/auth/login')
    return null
  }

  // Renderizar o conteúdo protegido
  return <>{children}</>
}
```

## Integração com o Backend FastAPI

### 1. Verificação de Token JWT

Crie um middleware para verificar tokens JWT do Supabase:

```python
# fastapi-backend/app/auth/jwt.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import PyJWTError
from app.config import settings
from app.services.supabase_service import supabase_client

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifica o token JWT do Supabase e retorna o usuário atual.
    """
    try:
        # Obter a chave pública do Supabase para verificação do JWT
        jwk_response = await supabase_client.auth.get_jwks()
        jwk = jwk_response['keys'][0]
        
        # Verificar o token
        payload = jwt.decode(
            credentials.credentials,
            jwk,
            algorithms=["RS256"],
            audience="authenticated",
            issuer=f"{settings.SUPABASE_URL}/auth/v1"
        )
        
        # Extrair o ID do usuário
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        return {"id": user_id}
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}"
        )
```

### 2. Uso do Middleware em Rotas Protegidas

```python
# fastapi-backend/app/api/v1/endpoints/user.py
from fastapi import APIRouter, Depends
from app.auth.jwt import get_current_user

router = APIRouter()

@router.get("/me")
async def get_user_profile(current_user = Depends(get_current_user)):
    """Retorna o perfil do usuário atual"""
    return {"user_id": current_user["id"]}
```

## Próximos Passos

Após a configuração da autenticação, os próximos passos são:

1. Implementar a integração com o frontend para gerenciamento de perfil
2. Configurar o armazenamento de arquivos (Storage)
3. Desenvolver as Edge Functions necessárias
4. Implementar a sincronização em tempo real

A autenticação é a base para todas as outras funcionalidades do sistema, garantindo que os usuários possam acessar seus dados de forma segura em diferentes dispositivos.
