# Configuração Inicial do Supabase

## 🎯 Objetivo
Estabelecer a configuração base do Supabase para o projeto StayFocus, incluindo cliente, autenticação e estrutura inicial.

## 📋 Pré-requisitos
- Conta Supabase criada
- Projeto Supabase configurado
- Variáveis de ambiente definidas

## 🔧 Implementação Passo a Passo

### 1. **Cliente Supabase Base**

#### Arquivo: `lib/supabase/client.ts`
```typescript
import { createClient } from '@supabase/supabase-js'
import type { Database } from './types'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    flowType: 'pkce'
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  },
  db: {
    schema: 'public'
  }
})

// Helper para verificar conexão
export const testConnection = async () => {
  try {
    const { data, error } = await supabase
      .from('_health')
      .select('*')
      .limit(1)
    
    return { connected: !error, error }
  } catch (error) {
    return { connected: false, error }
  }
}
```

### 2. **Tipos TypeScript Iniciais**

#### Arquivo: `lib/supabase/types.ts`
```typescript
export interface Database {
  public: {
    Tables: {
      user_profiles: {
        Row: UserProfile
        Insert: Omit<UserProfile, 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Omit<UserProfile, 'id' | 'created_at'>>
      }
      user_preferences: {
        Row: UserPreferences
        Insert: Omit<UserPreferences, 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Omit<UserPreferences, 'id' | 'user_id' | 'created_at'>>
      }
      // Outras tabelas serão adicionadas durante a migração
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}

export interface UserProfile {
  id: string
  nome: string | null
  email: string | null
  avatar_url: string | null
  created_at: string
  updated_at: string
}

export interface UserPreferences {
  id: string
  user_id: string
  alto_contraste: boolean
  reducao_estimulos: boolean
  texto_grande: boolean
  tema: 'light' | 'dark' | 'system'
  created_at: string
  updated_at: string
}

// Tipos de resposta padrão
export interface SupabaseResponse<T> {
  data: T | null
  error: {
    message: string
    details?: string
    hint?: string
    code?: string
  } | null
}

// Tipos para paginação
export interface PaginationParams {
  page?: number
  limit?: number
  offset?: number
}

export interface PaginatedResponse<T> {
  data: T[]
  count: number | null
  error: any
}
```

### 3. **Serviço de Autenticação**

#### Arquivo: `lib/supabase/auth.ts`
```typescript
import { supabase } from './client'
import type { User, Session } from '@supabase/supabase-js'

export interface AuthState {
  user: User | null
  session: Session | null
  loading: boolean
}

export const authService = {
  // Registrar novo usuário
  async signUp(email: string, password: string, userData?: any) {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: userData
        }
      })

      if (error) throw error

      // Criar perfil do usuário se registro bem-sucedido
      if (data.user && !error) {
        await this.createUserProfile(data.user, userData)
      }

      return { data, error: null }
    } catch (error: any) {
      return { data: null, error }
    }
  },

  // Login
  async signIn(email: string, password: string) {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      return { data, error }
    } catch (error: any) {
      return { data: null, error }
    }
  },

  // Logout
  async signOut() {
    try {
      const { error } = await supabase.auth.signOut()
      return { error }
    } catch (error: any) {
      return { error }
    }
  },

  // Obter usuário atual
  async getCurrentUser() {
    try {
      const { data: { user }, error } = await supabase.auth.getUser()
      return { user, error }
    } catch (error: any) {
      return { user: null, error }
    }
  },

  // Obter sessão atual
  async getCurrentSession() {
    try {
      const { data: { session }, error } = await supabase.auth.getSession()
      return { session, error }
    } catch (error: any) {
      return { session: null, error }
    }
  },

  // Resetar senha
  async resetPassword(email: string) {
    try {
      const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`,
      })

      return { data, error }
    } catch (error: any) {
      return { data: null, error }
    }
  },

  // Atualizar senha
  async updatePassword(newPassword: string) {
    try {
      const { data, error } = await supabase.auth.updateUser({
        password: newPassword
      })

      return { data, error }
    } catch (error: any) {
      return { data: null, error }
    }
  },

  // Criar perfil do usuário
  async createUserProfile(user: User, additionalData?: any) {
    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .insert({
          id: user.id,
          email: user.email,
          nome: additionalData?.nome || null,
          avatar_url: user.user_metadata?.avatar_url || null
        })

      if (error) throw error

      // Criar preferências padrão
      await supabase
        .from('user_preferences')
        .insert({
          user_id: user.id,
          alto_contraste: false,
          reducao_estimulos: false,
          texto_grande: false,
          tema: 'system'
        })

      return { data, error: null }
    } catch (error: any) {
      return { data: null, error }
    }
  },

  // Escutar mudanças de autenticação
  onAuthStateChange(callback: (event: string, session: Session | null) => void) {
    return supabase.auth.onAuthStateChange(callback)
  }
}
```

### 4. **Utilitários Base**

#### Arquivo: `lib/supabase/utils.ts`
```typescript
import { supabase } from './client'
import type { PaginatedResponse, PaginationParams } from './types'

// Utility para queries paginadas
export async function paginatedQuery<T>(
  query: any,
  params: PaginationParams = {}
): Promise<PaginatedResponse<T>> {
  const { page = 1, limit = 10 } = params
  const offset = (page - 1) * limit

  const { data, error, count } = await query
    .range(offset, offset + limit - 1)

  return { data: data || [], count, error }
}

// Utility para upload de arquivos
export async function uploadFile(
  bucket: string,
  path: string,
  file: File,
  options?: { upsert?: boolean }
) {
  try {
    const { data, error } = await supabase.storage
      .from(bucket)
      .upload(path, file, {
        upsert: options?.upsert || false
      })

    if (error) throw error

    // Obter URL pública
    const { data: urlData } = supabase.storage
      .from(bucket)
      .getPublicUrl(data.path)

    return { 
      data: { ...data, publicUrl: urlData.publicUrl }, 
      error: null 
    }
  } catch (error: any) {
    return { data: null, error }
  }
}

// Utility para deletar arquivos
export async function deleteFile(bucket: string, path: string) {
  try {
    const { data, error } = await supabase.storage
      .from(bucket)
      .remove([path])

    return { data, error }
  } catch (error: any) {
    return { data: null, error }
  }
}

// Utility para formatar erros do Supabase
export function formatSupabaseError(error: any): string {
  if (!error) return 'Erro desconhecido'
  
  // Erros comuns traduzidos
  const errorMessages: Record<string, string> = {
    'Invalid login credentials': 'Credenciais inválidas',
    'User already registered': 'Usuário já cadastrado',
    'Password should be at least 6 characters': 'Senha deve ter pelo menos 6 caracteres',
    'Email not confirmed': 'Email não confirmado',
    'Too many requests': 'Muitas tentativas. Tente novamente mais tarde',
    'Network error': 'Erro de conexão'
  }

  return errorMessages[error.message] || error.message || 'Erro interno'
}

// Utility para retry de operações
export async function retryOperation<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: any

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation()
    } catch (error) {
      lastError = error
      
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay * (i + 1)))
      }
    }
  }

  throw lastError
}

// Utility para validar UUID
export function isValidUUID(uuid: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
  return uuidRegex.test(uuid)
}

// Utility para sanitizar dados de entrada
export function sanitizeInput(input: any): any {
  if (typeof input === 'string') {
    return input.trim().slice(0, 1000) // Limitar tamanho
  }
  
  if (Array.isArray(input)) {
    return input.slice(0, 100).map(sanitizeInput) // Limitar array
  }
  
  if (typeof input === 'object' && input !== null) {
    const sanitized: any = {}
    for (const [key, value] of Object.entries(input)) {
      if (key.length <= 50) { // Limitar tamanho da chave
        sanitized[key] = sanitizeInput(value)
      }
    }
    return sanitized
  }
  
  return input
}
```

### 5. **Hook de Autenticação**

#### Arquivo: `lib/supabase/hooks/useAuth.ts`
```typescript
'use client'

import { useState, useEffect, useCallback } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { authService } from '../auth'

export interface UseAuthReturn {
  user: User | null
  session: Session | null
  loading: boolean
  signUp: (email: string, password: string, userData?: any) => Promise<any>
  signIn: (email: string, password: string) => Promise<any>
  signOut: () => Promise<any>
  resetPassword: (email: string) => Promise<any>
  updatePassword: (newPassword: string) => Promise<any>
}

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Obter sessão inicial
    const getInitialSession = async () => {
      const { session } = await authService.getCurrentSession()
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    }

    getInitialSession()

    // Escutar mudanças de autenticação
    const { data: { subscription } } = authService.onAuthStateChange(
      async (event, session) => {
        setSession(session)
        setUser(session?.user ?? null)
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  const signUp = useCallback(async (email: string, password: string, userData?: any) => {
    setLoading(true)
    const result = await authService.signUp(email, password, userData)
    setLoading(false)
    return result
  }, [])

  const signIn = useCallback(async (email: string, password: string) => {
    setLoading(true)
    const result = await authService.signIn(email, password)
    setLoading(false)
    return result
  }, [])

  const signOut = useCallback(async () => {
    setLoading(true)
    const result = await authService.signOut()
    setLoading(false)
    return result
  }, [])

  const resetPassword = useCallback(async (email: string) => {
    return await authService.resetPassword(email)
  }, [])

  const updatePassword = useCallback(async (newPassword: string) => {
    return await authService.updatePassword(newPassword)
  }, [])

  return {
    user,
    session,
    loading,
    signUp,
    signIn,
    signOut,
    resetPassword,
    updatePassword
  }
}
```

## ✅ Checklist de Validação

### Após implementar cada arquivo:
- [ ] `npm run build` passa sem erros
- [ ] `npm run type-check` passa sem erros
- [ ] Variáveis de ambiente estão configuradas
- [ ] Teste de conexão básica funciona

### Comandos de teste:
```bash
# Testar importações
node -e "console.log(require('./lib/supabase/client.ts'))"

# Testar conexão (se tiver dados)
node -e "
const { testConnection } = require('./lib/supabase/client.ts');
testConnection().then(console.log);
"
```

## 🚨 Troubleshooting

### Problemas Comuns:

1. **Erro de variáveis de ambiente**
   - Verificar se `.env.local` existe
   - Confirmar nomes das variáveis
   - Reiniciar servidor de desenvolvimento

2. **Erro de tipos TypeScript**
   - Verificar importação correta dos tipos
   - Confirmar se `@supabase/supabase-js` está instalado
   - Executar `npm run type-check`

3. **Erro de conexão**
   - Verificar URL e chave do Supabase
   - Confirmar se projeto está ativo
   - Testar no Supabase Dashboard

---

**Próximo:** [02 - Schema do Banco de Dados](./02-schema-banco.md)
