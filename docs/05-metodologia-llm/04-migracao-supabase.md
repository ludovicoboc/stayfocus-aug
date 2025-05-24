# 04 - Processo de Migração para Supabase

## 🎯 Estratégia de Migração

### Princípios Fundamentais:
1. **Migração incremental** - Uma store por vez
2. **Backward compatibility** - Manter funcionalidade durante migração
3. **Validação contínua** - Testar após cada etapa
4. **Rollback seguro** - Sempre manter versão funcional

## 🏗️ Fases da Migração

### Fase 1: Configuração da Infraestrutura
### Fase 2: Migração Individual das Stores
### Fase 3: Integração e Otimização
### Fase 4: Limpeza e Finalização

---

## 📋 FASE 1: Configuração da Infraestrutura

### 1.1 **Setup do Cliente Supabase**

#### A. Instalação e Configuração Base
```bash
# Instalar dependências
npm install @supabase/supabase-js @supabase/auth-helpers-nextjs
```

#### B. Criar Cliente Supabase
```typescript
// lib/supabase/client.ts
import { createClient } from '@supabase/supabase-js'
import { Database } from './types'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
})
```

#### C. Configurar Tipos TypeScript
```typescript
// lib/supabase/types.ts
export interface Database {
  public: {
    Tables: {
      // Será preenchido durante migração das stores
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
```

### 1.2 **Configuração de Autenticação**

#### A. Setup Auth Helper
```typescript
// lib/supabase/auth.ts
import { supabase } from './client'

export const authService = {
  async signUp(email: string, password: string) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    })
    return { data, error }
  },

  async signIn(email: string, password: string) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    return { data, error }
  },

  async signOut() {
    const { error } = await supabase.auth.signOut()
    return { error }
  },

  async getUser() {
    const { data: { user }, error } = await supabase.auth.getUser()
    return { user, error }
  }
}
```

### 1.3 **Configuração RLS (Row Level Security)**

#### A. Políticas Base de Segurança
```sql
-- Executar no Supabase SQL Editor

-- Habilitar RLS em todas as tabelas
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Política base: usuários só acessam seus próprios dados
CREATE POLICY "Users can view own data" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own data" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);
```

---

## 📋 FASE 2: Migração Individual das Stores

### 2.1 **Template de Migração por Store**

#### A. Padrão de Migração
```typescript
// Para cada store, seguir este padrão:

// 1. Criar tabela no Supabase
// 2. Definir tipos TypeScript
// 3. Criar serviços CRUD
// 4. Migrar store Zustand
// 5. Atualizar componentes
// 6. Testar funcionalidade
// 7. Validar performance
```

#### B. Ordem de Migração Recomendada
```typescript
const migrationOrder = [
  'userPreferencesStore',  // Mais simples, menos dependências
  'alimentacaoStore',      // Dados estruturados simples
  'autoconhecimentoStore', // Notas e categorias
  'sonoStore',            // Registros de sono
  'pomodoroStore',        // Timer e sessões
  'concursosStore',       // Mais complexa
  'estudosStore',         // Dependências com concursos
  'simuladoStore',        // Dependências múltiplas
  // Outras stores identificadas
]
```

### 2.2 **Migração: userPreferencesStore (Exemplo Completo)**

#### A. Análise da Store Atual
```bash
# LLM deve executar:
read_file(/app/stores/perfilStore.ts, 0, -1)
semantic_search("preferences theme contraste")
grep_search("perfilStore", includePattern="**/*.{ts,tsx}")
```

#### B. Criar Tabela no Supabase
```sql
-- SQL para executar no Supabase
CREATE TABLE user_preferences (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  alto_contraste BOOLEAN DEFAULT false,
  reducao_estimulos BOOLEAN DEFAULT false,
  texto_grande BOOLEAN DEFAULT false,
  tema TEXT DEFAULT 'system',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(user_id)
);

-- Habilitar RLS
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Políticas de segurança
CREATE POLICY "Users can view own preferences" ON user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own preferences" ON user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own preferences" ON user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

#### C. Definir Tipos TypeScript
```typescript
// lib/supabase/types.ts - Adicionar ao Database
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

// Atualizar Database interface
export interface Database {
  public: {
    Tables: {
      user_preferences: {
        Row: UserPreferences
        Insert: Omit<UserPreferences, 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Omit<UserPreferences, 'id' | 'user_id' | 'created_at'>>
      }
    }
  }
}
```

#### D. Criar Serviço CRUD
```typescript
// lib/supabase/services/userPreferencesService.ts
import { supabase } from '../client'
import { UserPreferences } from '../types'

export const userPreferencesService = {
  async get(userId: string): Promise<UserPreferences | null> {
    const { data, error } = await supabase
      .from('user_preferences')
      .select('*')
      .eq('user_id', userId)
      .single()

    if (error && error.code !== 'PGRST116') {
      throw error
    }

    return data
  },

  async upsert(preferences: Partial<UserPreferences> & { user_id: string }): Promise<UserPreferences> {
    const { data, error } = await supabase
      .from('user_preferences')
      .upsert(preferences)
      .select()
      .single()

    if (error) throw error
    return data
  },

  async subscribe(userId: string, callback: (preferences: UserPreferences) => void) {
    return supabase
      .channel('user_preferences_changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'user_preferences',
          filter: `user_id=eq.${userId}`
        },
        (payload) => {
          callback(payload.new as UserPreferences)
        }
      )
      .subscribe()
  }
}
```

#### E. Migrar Store Zustand
```typescript
// stores/userPreferencesStore.ts - Nova versão
import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'
import { userPreferencesService } from '../lib/supabase/services/userPreferencesService'
import { UserPreferences } from '../lib/supabase/types'

interface UserPreferencesState {
  preferences: UserPreferences | null
  isLoading: boolean
  error: string | null
  
  // Actions
  loadPreferences: (userId: string) => Promise<void>
  updatePreferences: (updates: Partial<UserPreferences>) => Promise<void>
  subscribeToChanges: (userId: string) => () => void
}

export const useUserPreferencesStore = create<UserPreferencesState>()(
  subscribeWithSelector((set, get) => ({
    preferences: null,
    isLoading: false,
    error: null,

    loadPreferences: async (userId: string) => {
      set({ isLoading: true, error: null })
      try {
        const preferences = await userPreferencesService.get(userId)
        set({ preferences, isLoading: false })
      } catch (error) {
        set({ error: error.message, isLoading: false })
      }
    },

    updatePreferences: async (updates: Partial<UserPreferences>) => {
      const { preferences } = get()
      if (!preferences) return

      set({ isLoading: true, error: null })
      try {
        const updatedPreferences = await userPreferencesService.upsert({
          ...preferences,
          ...updates,
          updated_at: new Date().toISOString()
        })
        set({ preferences: updatedPreferences, isLoading: false })
      } catch (error) {
        set({ error: error.message, isLoading: false })
      }
    },

    subscribeToChanges: (userId: string) => {
      const subscription = userPreferencesService.subscribe(userId, (preferences) => {
        set({ preferences })
      })

      return () => {
        subscription.unsubscribe()
      }
    }
  }))
)
```

#### F. Validação da Migração
```typescript
// Teste da migração
// test/userPreferencesStore.test.ts
import { renderHook, act } from '@testing-library/react'
import { useUserPreferencesStore } from '../stores/userPreferencesStore'

describe('UserPreferencesStore Migration', () => {
  it('should load preferences from Supabase', async () => {
    const { result } = renderHook(() => useUserPreferencesStore())
    
    await act(async () => {
      await result.current.loadPreferences('test-user-id')
    })

    expect(result.current.isLoading).toBe(false)
    expect(result.current.preferences).toBeDefined()
  })

  it('should update preferences', async () => {
    const { result } = renderHook(() => useUserPreferencesStore())
    
    await act(async () => {
      await result.current.updatePreferences({ alto_contraste: true })
    })

    expect(result.current.preferences?.alto_contraste).toBe(true)
  })
})
```

### 2.3 **Template para Outras Stores**

Para cada store subsequente, repetir processo:

#### A. Checklist por Store:
- [ ] Analisar store atual
- [ ] Criar schema SQL
- [ ] Definir tipos TypeScript
- [ ] Implementar serviço CRUD
- [ ] Migrar store Zustand
- [ ] Atualizar componentes que usam
- [ ] Executar testes
- [ ] Validar performance
- [ ] Documentar mudanças

---

## 📋 FASE 3: Integração e Otimização

### 3.1 **Sincronização Real-time**

#### A. Configurar Realtime Global
```typescript
// lib/supabase/realtime.ts
import { supabase } from './client'

export const setupRealtimeSubscriptions = (userId: string) => {
  const subscriptions = []

  // Para cada tabela que precisa de realtime
  const tables = [
    'user_preferences',
    'refeicoes',
    'notas_autoconhecimento',
    // outras tabelas
  ]

  tables.forEach(table => {
    const subscription = supabase
      .channel(`${table}_changes`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table,
          filter: `user_id=eq.${userId}`
        },
        (payload) => {
          // Notificar stores relevantes
          window.dispatchEvent(new CustomEvent(`${table}_changed`, {
            detail: payload
          }))
        }
      )
      .subscribe()

    subscriptions.push(subscription)
  })

  return () => {
    subscriptions.forEach(sub => sub.unsubscribe())
  }
}
```

### 3.2 **Otimização de Performance**

#### A. Caching e Debouncing
```typescript
// lib/supabase/cache.ts
import { LRUCache } from 'lru-cache'

const cache = new LRUCache<string, any>({
  max: 500,
  ttl: 1000 * 60 * 5 // 5 minutos
})

export const cachedQuery = async <T>(
  key: string,
  queryFn: () => Promise<T>,
  ttl?: number
): Promise<T> => {
  const cached = cache.get(key)
  if (cached) return cached

  const result = await queryFn()
  cache.set(key, result, ttl)
  return result
}
```

---

## 📋 FASE 4: Limpeza e Finalização

### 4.1 **Remoção de Código Legacy**

#### A. Backup e Limpeza
```bash
# Backup das stores antigas
mkdir backup/stores-legacy
cp -r app/stores/* backup/stores-legacy/

# Remover persist middleware não usado
# Remover localStorage calls antigas
# Limpar imports não utilizados
```

### 4.2 **Validação Final**

#### A. Checklist de Migração Completa:
- [ ] Todas as stores migradas
- [ ] Todos os componentes funcionando
- [ ] Testes passando
- [ ] Performance aceitável
- [ ] Segurança RLS implementada
- [ ] Realtime funcionando
- [ ] Documentação atualizada

## 🚨 Pontos Críticos para LLM

### ⚠️ NUNCA:
- Migrar múltiplas stores simultaneamente
- Deletar código antes de validar migração
- Pular testes de validação
- Ignorar erros de TypeScript
- Fazer deploy sem backup

### ✅ SEMPRE:
- Executar um comando por vez
- Validar cada etapa antes de prosseguir
- Manter backup de código funcional
- Testar no browser após mudanças
- Documentar problemas encontrados

---

**Anterior:** [03 - Análise do Contexto](./03-analise-contexto.md) | **Próximo:** [05 - Implementação SATI](./05-implementacao-sati.md)
