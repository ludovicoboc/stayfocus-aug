# Integração com o Frontend

## Contexto

A integração do Supabase com o frontend do StayFocus é uma etapa crucial para a migração do armazenamento local para um backend robusto. Atualmente, o StayFocus utiliza o Zustand com persistência local para gerenciar o estado da aplicação. A migração para o Supabase requer a refatoração das stores Zustand para usar o Supabase como fonte de dados, mantendo a mesma API para os componentes existentes.

Além disso, é necessário implementar mecanismos de cache local para garantir o funcionamento offline da aplicação, com sincronização automática quando o usuário voltar a ficar online.

## Atualização do Cliente Supabase

O primeiro passo é garantir que o cliente Supabase esteja corretamente configurado e disponível em toda a aplicação:

```typescript
// app/lib/supabase/client.ts
import { createClient } from '@supabase/supabase-js'
import { Database } from './database.types'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Faltam variáveis de ambiente do Supabase. Verifique o arquivo .env.local')
}

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
})
```

## Refatoração das Stores Zustand

### 1. Criação de Hooks de Dados Híbridos

Para facilitar a transição e garantir o funcionamento offline, vamos criar um hook personalizado que combina o Zustand com o Supabase:

```typescript
// app/hooks/useHybridStore.ts
import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase/client'
import { useAuth } from './useAuth'

export function useHybridStore<T>({
  tableName,
  localStore,
  idField = 'id',
  userIdField = 'user_id',
  orderBy = { column: 'created_at', ascending: false }
}: {
  tableName: string
  localStore: any
  idField?: string
  userIdField?: string
  orderBy?: { column: string, ascending: boolean }
}) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [initialized, setInitialized] = useState(false)
  const { user } = useAuth()
  
  // Obter dados e funções da store local
  const localData = localStore((state: any) => state)
  
  // Carregar dados do Supabase na inicialização
  useEffect(() => {
    if (user && !initialized) {
      loadDataFromSupabase()
    }
  }, [user, initialized])
  
  // Função para carregar dados do Supabase
  const loadDataFromSupabase = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Buscar dados do usuário atual
      const { data, error } = await supabase
        .from(tableName)
        .select('*')
        .eq(userIdField, user?.id)
        .order(orderBy.column, { ascending: orderBy.ascending })
      
      if (error) {
        throw error
      }
      
      // Atualizar store local com dados do Supabase
      if (data && data.length > 0) {
        // Remover funções antes de atualizar a store
        const dataWithoutFunctions = data.map((item: any) => {
          const newItem = { ...item }
          Object.keys(newItem).forEach(key => {
            if (typeof newItem[key] === 'function') {
              delete newItem[key]
            }
          })
          return newItem
        })
        
        // Atualizar store local
        localStore.setState((state: any) => ({
          ...state,
          items: dataWithoutFunctions
        }))
      }
      
      setInitialized(true)
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar dados')
      console.error('Erro ao carregar dados do Supabase:', err)
    } finally {
      setLoading(false)
    }
  }
  
  // Função para adicionar item
  const addItem = async (item: Omit<T, typeof idField | typeof userIdField>) => {
    try {
      setError(null)
      
      // Verificar autenticação
      if (!user) {
        // Se não estiver autenticado, apenas adicionar localmente
        const newItem = {
          ...item,
          [idField]: `local_${Date.now()}`,
          [userIdField]: 'local',
          _isOffline: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        
        // Adicionar à store local
        localStore.getState().addItem(newItem)
        
        return { data: newItem, isOffline: true }
      }
      
      // Se estiver autenticado, adicionar ao Supabase
      const { data, error } = await supabase
        .from(tableName)
        .insert({
          ...item,
          [userIdField]: user.id
        })
        .select()
        .single()
      
      if (error) {
        throw error
      }
      
      // Adicionar à store local
      localStore.getState().addItem(data)
      
      return { data, isOffline: false }
    } catch (err: any) {
      setError(err.message || 'Erro ao adicionar item')
      console.error('Erro ao adicionar item:', err)
      
      // Em caso de erro, adicionar localmente com flag offline
      const newItem = {
        ...item,
        [idField]: `local_${Date.now()}`,
        [userIdField]: user?.id || 'local',
        _isOffline: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      
      // Adicionar à store local
      localStore.getState().addItem(newItem)
      
      return { data: newItem, isOffline: true, error: err }
    }
  }
  
  // Função para atualizar item
  const updateItem = async (id: string, updates: Partial<T>) => {
    try {
      setError(null)
      
      // Verificar se é um item offline
      const isLocalId = id.startsWith('local_')
      
      if (isLocalId || !user) {
        // Atualizar apenas localmente
        localStore.getState().updateItem(id, {
          ...updates,
          _isOffline: true,
          updated_at: new Date().toISOString()
        })
        
        return { isOffline: true }
      }
      
      // Atualizar no Supabase
      const { data, error } = await supabase
        .from(tableName)
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq(idField, id)
        .select()
        .single()
      
      if (error) {
        throw error
      }
      
      // Atualizar na store local
      localStore.getState().updateItem(id, data)
      
      return { data, isOffline: false }
    } catch (err: any) {
      setError(err.message || 'Erro ao atualizar item')
      console.error('Erro ao atualizar item:', err)
      
      // Em caso de erro, atualizar localmente com flag offline
      localStore.getState().updateItem(id, {
        ...updates,
        _isOffline: true,
        updated_at: new Date().toISOString()
      })
      
      return { isOffline: true, error: err }
    }
  }
  
  // Função para remover item
  const removeItem = async (id: string) => {
    try {
      setError(null)
      
      // Verificar se é um item offline
      const isLocalId = id.startsWith('local_')
      
      if (isLocalId || !user) {
        // Remover apenas localmente
        localStore.getState().removeItem(id)
        
        return { isOffline: true }
      }
      
      // Remover do Supabase
      const { error } = await supabase
        .from(tableName)
        .delete()
        .eq(idField, id)
      
      if (error) {
        throw error
      }
      
      // Remover da store local
      localStore.getState().removeItem(id)
      
      return { isOffline: false }
    } catch (err: any) {
      setError(err.message || 'Erro ao remover item')
      console.error('Erro ao remover item:', err)
      
      // Em caso de erro, marcar como offline para remoção posterior
      localStore.getState().updateItem(id, {
        _isOffline: true,
        _pendingDeletion: true,
        updated_at: new Date().toISOString()
      })
      
      return { isOffline: true, error: err }
    }
  }
  
  // Função para sincronizar dados offline
  const syncOfflineData = async () => {
    if (!user) return { synced: 0, errors: 0 }
    
    try {
      setLoading(true)
      setError(null)
      
      const items = localStore.getState().items || []
      const offlineItems = items.filter((item: any) => item._isOffline)
      
      if (offlineItems.length === 0) {
        return { synced: 0, errors: 0 }
      }
      
      let synced = 0
      let errors = 0
      
      for (const item of offlineItems) {
        try {
          if (item._pendingDeletion) {
            // Item marcado para exclusão
            if (!item[idField].startsWith('local_')) {
              await supabase
                .from(tableName)
                .delete()
                .eq(idField, item[idField])
            }
            
            // Remover da store local
            localStore.getState().removeItem(item[idField])
          } else if (item[idField].startsWith('local_')) {
            // Novo item criado offline
            const { id, _isOffline, _pendingDeletion, ...itemData } = item
            
            const { data, error } = await supabase
              .from(tableName)
              .insert({
                ...itemData,
                [userIdField]: user.id
              })
              .select()
              .single()
            
            if (error) throw error
            
            // Remover versão offline e adicionar versão do servidor
            localStore.getState().removeItem(id)
            localStore.getState().addItem(data)
          } else {
            // Item existente atualizado offline
            const { _isOffline, _pendingDeletion, ...itemData } = item
            
            await supabase
              .from(tableName)
              .update(itemData)
              .eq(idField, item[idField])
          }
          
          synced++
        } catch (err) {
          console.error('Erro ao sincronizar item:', err)
          errors++
        }
      }
      
      return { synced, errors }
    } catch (err: any) {
      setError(err.message || 'Erro ao sincronizar dados offline')
      console.error('Erro ao sincronizar dados offline:', err)
      return { synced: 0, errors: -1 }
    } finally {
      setLoading(false)
    }
  }
  
  return {
    ...localData,
    loading,
    error,
    initialized,
    addItem,
    updateItem,
    removeItem,
    syncOfflineData,
    refreshData: loadDataFromSupabase
  }
}
```

### 2. Refatoração da Store de Hiperfocos

Vamos refatorar a store de hiperfocos como exemplo:

```typescript
// app/stores/hiperfocosStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Tarefa {
  id: string
  texto: string
  concluida: boolean
  cor?: string
}

export interface Hiperfoco {
  id: string
  titulo: string
  descricao: string
  tarefas: Tarefa[]
  subTarefas: Record<string, Tarefa[]>
  cor: string
  dataCriacao: string
  tempoLimite?: number
}

interface HiperfocosState {
  hiperfocos: Hiperfoco[]
  
  // Ações para hiperfocos
  adicionarHiperfoco: (hiperfoco: Omit<Hiperfoco, 'id' | 'dataCriacao'>) => void
  atualizarHiperfoco: (id: string, atualizacoes: Partial<Hiperfoco>) => void
  removerHiperfoco: (id: string) => void
  
  // Ações para tarefas
  adicionarTarefa: (hiperfocoId: string, tarefa: Omit<Tarefa, 'id'>) => void
  atualizarTarefa: (hiperfocoId: string, tarefaId: string, atualizacoes: Partial<Tarefa>) => void
  removerTarefa: (hiperfocoId: string, tarefaId: string) => void
  toggleTarefaConcluida: (hiperfocoId: string, tarefaId: string) => void
  
  // Ações para subtarefas
  adicionarSubTarefa: (hiperfocoId: string, tarefaPaiId: string, subtarefa: Omit<Tarefa, 'id'>) => void
  atualizarSubTarefa: (hiperfocoId: string, tarefaPaiId: string, subtarefaId: string, atualizacoes: Partial<Tarefa>) => void
  removerSubTarefa: (hiperfocoId: string, tarefaPaiId: string, subtarefaId: string) => void
  toggleSubTarefaConcluida: (hiperfocoId: string, tarefaPaiId: string, subtarefaId: string) => void
}

export const useHiperfocosStore = create<HiperfocosState>()(
  persist(
    (set) => ({
      hiperfocos: [],
      
      // Implementações das ações para hiperfocos
      adicionarHiperfoco: (hiperfoco) => set((state) => ({
        hiperfocos: [
          ...state.hiperfocos,
          {
            ...hiperfoco,
            id: Date.now().toString(),
            dataCriacao: new Date().toISOString(),
            tarefas: [],
            subTarefas: {}
          }
        ]
      })),
      
      atualizarHiperfoco: (id, atualizacoes) => set((state) => ({
        hiperfocos: state.hiperfocos.map((h) =>
          h.id === id ? { ...h, ...atualizacoes } : h
        )
      })),
      
      removerHiperfoco: (id) => set((state) => ({
        hiperfocos: state.hiperfocos.filter((h) => h.id !== id)
      })),
      
      // Implementações das ações para tarefas
      adicionarTarefa: (hiperfocoId, tarefa) => set((state) => ({
        hiperfocos: state.hiperfocos.map((h) => {
          if (h.id === hiperfocoId) {
            return {
              ...h,
              tarefas: [
                ...h.tarefas,
                {
                  ...tarefa,
                  id: Date.now().toString()
                }
              ]
            }
          }
          return h
        })
      })),
      
      // Implementações das demais ações...
      atualizarTarefa: (hiperfocoId, tarefaId, atualizacoes) => set((state) => ({
        hiperfocos: state.hiperfocos.map((h) => {
          if (h.id === hiperfocoId) {
            return {
              ...h,
              tarefas: h.tarefas.map((t) =>
                t.id === tarefaId ? { ...t, ...atualizacoes } : t
              )
            }
          }
          return h
        })
      })),
      
      removerTarefa: (hiperfocoId, tarefaId) => set((state) => ({
        hiperfocos: state.hiperfocos.map((h) => {
          if (h.id === hiperfocoId) {
            return {
              ...h,
              tarefas: h.tarefas.filter((t) => t.id !== tarefaId),
              // Também remover subtarefas associadas
              subTarefas: {
                ...h.subTarefas,
                [tarefaId]: undefined
              }
            }
          }
          return h
        })
      })),
      
      toggleTarefaConcluida: (hiperfocoId, tarefaId) => set((state) => ({
        hiperfocos: state.hiperfocos.map((h) => {
          if (h.id === hiperfocoId) {
            return {
              ...h,
              tarefas: h.tarefas.map((t) =>
                t.id === tarefaId ? { ...t, concluida: !t.concluida } : t
              )
            }
          }
          return h
        })
      })),
      
      // Implementações das ações para subtarefas...
      adicionarSubTarefa: (hiperfocoId, tarefaPaiId, subtarefa) => set((state) => ({
        hiperfocos: state.hiperfocos.map((h) => {
          if (h.id === hiperfocoId) {
            const subTarefasAtuais = h.subTarefas[tarefaPaiId] || []
            return {
              ...h,
              subTarefas: {
                ...h.subTarefas,
                [tarefaPaiId]: [
                  ...subTarefasAtuais,
                  {
                    ...subtarefa,
                    id: Date.now().toString()
                  }
                ]
              }
            }
          }
          return h
        })
      })),
      
      // Implementações das demais ações para subtarefas...
      atualizarSubTarefa: (hiperfocoId, tarefaPaiId, subtarefaId, atualizacoes) => set((state) => ({
        hiperfocos: state.hiperfocos.map((h) => {
          if (h.id === hiperfocoId && h.subTarefas[tarefaPaiId]) {
            return {
              ...h,
              subTarefas: {
                ...h.subTarefas,
                [tarefaPaiId]: h.subTarefas[tarefaPaiId].map((st) =>
                  st.id === subtarefaId ? { ...st, ...atualizacoes } : st
                )
              }
            }
          }
          return h
        })
      })),
      
      removerSubTarefa: (hiperfocoId, tarefaPaiId, subtarefaId) => set((state) => ({
        hiperfocos: state.hiperfocos.map((h) => {
          if (h.id === hiperfocoId && h.subTarefas[tarefaPaiId]) {
            return {
              ...h,
              subTarefas: {
                ...h.subTarefas,
                [tarefaPaiId]: h.subTarefas[tarefaPaiId].filter((st) => st.id !== subtarefaId)
              }
            }
          }
          return h
        })
      })),
      
      toggleSubTarefaConcluida: (hiperfocoId, tarefaPaiId, subtarefaId) => set((state) => ({
        hiperfocos: state.hiperfocos.map((h) => {
          if (h.id === hiperfocoId && h.subTarefas[tarefaPaiId]) {
            return {
              ...h,
              subTarefas: {
                ...h.subTarefas,
                [tarefaPaiId]: h.subTarefas[tarefaPaiId].map((st) =>
                  st.id === subtarefaId ? { ...st, concluida: !st.concluida } : st
                )
              }
            }
          }
          return h
        })
      }))
    }),
    {
      name: 'hiperfocos-storage',
    }
  )
)
```

### 3. Uso do Hook Híbrido nos Componentes

```tsx
// app/components/hiperfocos/GerenciadorHiperfocos.tsx
import { useEffect } from 'react'
import { useHiperfocosStore } from '../../stores/hiperfocosStore'
import { useHybridStore } from '../../hooks/useHybridStore'
import { useAuth } from '../../hooks/useAuth'
import { useOnlineStatus } from '../../hooks/useOnlineStatus'

export function GerenciadorHiperfocos() {
  const hiperfocosStore = useHiperfocosStore()
  const { user } = useAuth()
  const isOnline = useOnlineStatus()
  
  // Usar o hook híbrido para hiperfocos
  const {
    loading,
    error,
    addItem: adicionarHiperfoco,
    updateItem: atualizarHiperfoco,
    removeItem: removerHiperfoco,
    syncOfflineData,
    refreshData
  } = useHybridStore({
    tableName: 'hiperfoco_projetos',
    localStore: useHiperfocosStore,
    idField: 'id',
    userIdField: 'user_id'
  })
  
  // Sincronizar dados offline quando o usuário ficar online
  useEffect(() => {
    if (isOnline && user) {
      syncOfflineData().then(({ synced, errors }) => {
        if (synced > 0) {
          console.log(`Sincronizados ${synced} itens offline (${errors} erros)`)
          // Atualizar dados após sincronização
          refreshData()
        }
      })
    }
  }, [isOnline, user])
  
  // Resto do componente...
  
  return (
    <div>
      {loading && <p>Carregando hiperfocos...</p>}
      {error && <p>Erro: {error}</p>}
      
      {/* Componentes de UI para gerenciar hiperfocos */}
    </div>
  )
}
```

## Implementação de Sincronização em Tempo Real

Para manter os dados sincronizados entre dispositivos, vamos implementar a funcionalidade de tempo real do Supabase:

```typescript
// app/hooks/useRealtimeData.ts
import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase/client'
import { useAuth } from './useAuth'

export function useRealtimeData<T>({
  tableName,
  onInsert,
  onUpdate,
  onDelete,
  userIdField = 'user_id'
}: {
  tableName: string
  onInsert?: (item: T) => void
  onUpdate?: (item: T) => void
  onDelete?: (id: string) => void
  userIdField?: string
}) {
  const [subscribed, setSubscribed] = useState(false)
  const { user } = useAuth()
  
  useEffect(() => {
    if (!user) return
    
    // Inscrever-se para atualizações em tempo real
    const channel = supabase
      .channel(`public:${tableName}:${userIdField}=eq.${user.id}`)
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: tableName,
        filter: `${userIdField}=eq.${user.id}`
      }, (payload) => {
        if (onInsert) onInsert(payload.new as T)
      })
      .on('postgres_changes', {
        event: 'UPDATE',
        schema: 'public',
        table: tableName,
        filter: `${userIdField}=eq.${user.id}`
      }, (payload) => {
        if (onUpdate) onUpdate(payload.new as T)
      })
      .on('postgres_changes', {
        event: 'DELETE',
        schema: 'public',
        table: tableName,
        filter: `${userIdField}=eq.${user.id}`
      }, (payload) => {
        if (onDelete) onDelete(payload.old.id as string)
      })
      .subscribe((status) => {
        setSubscribed(status === 'SUBSCRIBED')
      })
    
    return () => {
      supabase.removeChannel(channel)
    }
  }, [tableName, user, onInsert, onUpdate, onDelete, userIdField])
  
  return { subscribed }
}
```

## Implementação de Cache Local para Funcionamento Offline

Para garantir o funcionamento offline, vamos implementar um mecanismo de cache local:

```typescript
// app/hooks/useOfflineCache.ts
import { useState, useEffect } from 'react'
import { useAuth } from './useAuth'
import { useOnlineStatus } from './useOnlineStatus'

export function useOfflineCache<T>({
  key,
  getData,
  syncData,
  dependencies = []
}: {
  key: string
  getData: () => Promise<T[]>
  syncData: (items: T[]) => Promise<void>
  dependencies?: any[]
}) {
  const [data, setData] = useState<T[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuth()
  const isOnline = useOnlineStatus()
  
  // Carregar dados
  useEffect(() => {
    if (!user) return
    
    const loadData = async () => {
      setLoading(true)
      setError(null)
      
      try {
        // Tentar carregar do cache primeiro
        const cachedData = localStorage.getItem(`offline_cache_${key}_${user.id}`)
        
        if (cachedData) {
          setData(JSON.parse(cachedData))
        }
        
        // Se estiver online, buscar dados atualizados
        if (isOnline) {
          const freshData = await getData()
          setData(freshData)
          
          // Atualizar cache
          localStorage.setItem(`offline_cache_${key}_${user.id}`, JSON.stringify(freshData))
        }
      } catch (err: any) {
        setError(err.message || 'Erro ao carregar dados')
        console.error('Erro ao carregar dados:', err)
      } finally {
        setLoading(false)
      }
    }
    
    loadData()
  }, [key, user, isOnline, ...dependencies])
  
  // Sincronizar dados offline quando ficar online
  useEffect(() => {
    if (isOnline && user && data.length > 0) {
      const offlineItems = data.filter((item: any) => item._isOffline)
      
      if (offlineItems.length > 0) {
        syncData(offlineItems)
          .then(() => {
            console.log(`Sincronizados ${offlineItems.length} itens offline`)
          })
          .catch((err) => {
            console.error('Erro ao sincronizar dados offline:', err)
          })
      }
    }
  }, [isOnline, user])
  
  return { data, loading, error }
}
```

## Próximos Passos

Após a integração com o frontend, os próximos passos são:

1. Configurar a sincronização em tempo real para todas as entidades
2. Implementar mecanismos de resolução de conflitos
3. Otimizar o desempenho das consultas
4. Implementar testes de integração

A integração com o frontend é uma etapa crítica para garantir que a migração para o Supabase seja transparente para os usuários, mantendo a mesma experiência de uso e adicionando novas funcionalidades como sincronização entre dispositivos.
