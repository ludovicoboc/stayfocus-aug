# Configuração de Realtime

## Contexto

A funcionalidade Realtime do Supabase permite a sincronização em tempo real de dados entre diferentes clientes, possibilitando que alterações feitas por um usuário sejam imediatamente refletidas em todos os dispositivos conectados. Isso é especialmente importante para o StayFocus, que visa oferecer uma experiência fluida de uso em múltiplos dispositivos.

O Supabase Realtime é baseado em WebSockets e utiliza o sistema de replicação lógica do PostgreSQL para detectar alterações no banco de dados e transmiti-las aos clientes conectados. Isso permite implementar funcionalidades como:

1. Atualização instantânea de dados em múltiplos dispositivos
2. Notificações em tempo real para eventos importantes
3. Colaboração entre usuários (em funcionalidades futuras)
4. Sincronização de estado da aplicação

## Habilitando o Realtime no Supabase

### 1. Configuração no Painel do Supabase

Para habilitar o Realtime para as tabelas do StayFocus:

1. Acesse o painel do Supabase e navegue até "Database" > "Replication"
2. Na seção "Realtime", habilite a replicação para as tabelas principais:
   - user_profiles
   - user_preferences
   - refeicoes
   - hidratacao
   - notas_autoconhecimento
   - concursos
   - conteudo_programatico
   - hiperfoco_projetos
   - hiperfoco_tarefas
   - pomodoro_sessoes
   - registros_sono
   - medicamentos

Alternativamente, você pode habilitar o Realtime via SQL:

```sql
-- Habilitar publicação para todas as tabelas
ALTER PUBLICATION supabase_realtime ADD TABLE user_profiles, user_preferences, refeicoes, hidratacao, notas_autoconhecimento, concursos, conteudo_programatico, hiperfoco_projetos, hiperfoco_tarefas, pomodoro_sessoes, registros_sono, medicamentos;

-- Ou habilitar para tabelas específicas
ALTER PUBLICATION supabase_realtime ADD TABLE hiperfoco_projetos, hiperfoco_tarefas;
```

### 2. Configuração de Canais

Para otimizar o desempenho e reduzir o tráfego de dados, é recomendável configurar canais específicos para cada tipo de entidade:

```sql
-- Criar canais para cada tipo de entidade
BEGIN;

-- Canal para hiperfocos
INSERT INTO realtime.channels (name, filters)
VALUES (
  'hiperfocos',
  ARRAY[
    realtime.filter('hiperfoco_projetos', 'user_id', 'eq'),
    realtime.filter('hiperfoco_tarefas', 'projeto_id', 'eq')
  ]
);

-- Canal para concursos
INSERT INTO realtime.channels (name, filters)
VALUES (
  'concursos',
  ARRAY[
    realtime.filter('concursos', 'user_id', 'eq'),
    realtime.filter('conteudo_programatico', 'concurso_id', 'eq')
  ]
);

-- Canal para alimentação
INSERT INTO realtime.channels (name, filters)
VALUES (
  'alimentacao',
  ARRAY[
    realtime.filter('refeicoes', 'user_id', 'eq'),
    realtime.filter('hidratacao', 'user_id', 'eq')
  ]
);

-- Canal para autoconhecimento
INSERT INTO realtime.channels (name, filters)
VALUES (
  'autoconhecimento',
  ARRAY[
    realtime.filter('notas_autoconhecimento', 'user_id', 'eq')
  ]
);

-- Canal para sono
INSERT INTO realtime.channels (name, filters)
VALUES (
  'sono',
  ARRAY[
    realtime.filter('registros_sono', 'user_id', 'eq'),
    realtime.filter('lembretes_sono', 'user_id', 'eq')
  ]
);

-- Canal para medicamentos
INSERT INTO realtime.channels (name, filters)
VALUES (
  'medicamentos',
  ARRAY[
    realtime.filter('medicamentos', 'user_id', 'eq'),
    realtime.filter('registros_medicamentos', 'medicamento_id', 'eq')
  ]
);

COMMIT;
```

## Implementação no Frontend

### 1. Hook para Subscrição em Tempo Real

Vamos criar um hook personalizado para facilitar a subscrição a eventos em tempo real:

```typescript
// app/hooks/useRealtimeSubscription.ts
import { useEffect, useState } from 'react'
import { RealtimeChannel } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase/client'
import { useAuth } from './useAuth'

type RealtimeEvent = 'INSERT' | 'UPDATE' | 'DELETE' | '*'

interface RealtimeSubscriptionOptions {
  table: string
  event?: RealtimeEvent
  schema?: string
  filter?: string
  filterValue?: string | number
  onEvent: (payload: any) => void
}

export function useRealtimeSubscription({
  table,
  event = '*',
  schema = 'public',
  filter,
  filterValue,
  onEvent
}: RealtimeSubscriptionOptions) {
  const [channel, setChannel] = useState<RealtimeChannel | null>(null)
  const [subscribed, setSubscribed] = useState(false)
  const { user } = useAuth()

  useEffect(() => {
    if (!user) return

    // Construir filtro
    let filterString = ''
    if (filter && filterValue) {
      filterString = `${filter}=eq.${filterValue}`
    } else if (table !== 'user_profiles') {
      // Por padrão, filtrar por user_id
      filterString = `user_id=eq.${user.id}`
    }

    // Criar canal
    const channelName = `${schema}:${table}:${filterString}`
    const newChannel = supabase.channel(channelName)

    // Configurar evento
    if (event === '*') {
      // Subscrever a todos os eventos
      newChannel.on('postgres_changes', {
        event: 'INSERT',
        schema,
        table,
        filter: filterString
      }, (payload) => onEvent({ type: 'INSERT', data: payload.new }))
      .on('postgres_changes', {
        event: 'UPDATE',
        schema,
        table,
        filter: filterString
      }, (payload) => onEvent({ type: 'UPDATE', data: payload.new, old: payload.old }))
      .on('postgres_changes', {
        event: 'DELETE',
        schema,
        table,
        filter: filterString
      }, (payload) => onEvent({ type: 'DELETE', data: payload.old }))
    } else {
      // Subscrever a um evento específico
      newChannel.on('postgres_changes', {
        event,
        schema,
        table,
        filter: filterString
      }, (payload) => {
        if (event === 'INSERT') onEvent({ type: 'INSERT', data: payload.new })
        else if (event === 'UPDATE') onEvent({ type: 'UPDATE', data: payload.new, old: payload.old })
        else if (event === 'DELETE') onEvent({ type: 'DELETE', data: payload.old })
      })
    }

    // Subscrever ao canal
    newChannel.subscribe((status) => {
      setSubscribed(status === 'SUBSCRIBED')
    })

    setChannel(newChannel)

    // Limpar subscrição ao desmontar
    return () => {
      if (newChannel) {
        supabase.removeChannel(newChannel)
      }
    }
  }, [table, event, schema, filter, filterValue, user, onEvent])

  return { subscribed }
}
```

### 2. Hook para Dados em Tempo Real

Vamos criar um hook que combina a busca inicial de dados com atualizações em tempo real:

```typescript
// app/hooks/useRealtimeData.ts
import { useState, useEffect, useCallback } from 'react'
import { supabase } from '../lib/supabase/client'
import { useAuth } from './useAuth'
import { useRealtimeSubscription } from './useRealtimeSubscription'

export function useRealtimeData<T>({
  table,
  select = '*',
  filter,
  filterValue,
  orderBy,
  orderDirection = 'desc'
}: {
  table: string
  select?: string
  filter?: string
  filterValue?: string | number
  orderBy?: string
  orderDirection?: 'asc' | 'desc'
}) {
  const [data, setData] = useState<T[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuth()

  // Função para buscar dados
  const fetchData = useCallback(async () => {
    if (!user) return

    try {
      setLoading(true)
      setError(null)

      // Construir consulta
      let query = supabase
        .from(table)
        .select(select)

      // Aplicar filtro personalizado se fornecido
      if (filter && filterValue) {
        query = query.eq(filter, filterValue)
      } else if (table !== 'user_profiles') {
        // Por padrão, filtrar por user_id
        query = query.eq('user_id', user.id)
      }

      // Aplicar ordenação se fornecida
      if (orderBy) {
        query = query.order(orderBy, { ascending: orderDirection === 'asc' })
      }

      const { data: result, error: queryError } = await query

      if (queryError) {
        throw queryError
      }

      setData(result as T[])
    } catch (err: any) {
      setError(err.message || 'Erro ao buscar dados')
      console.error(`Erro ao buscar dados da tabela ${table}:`, err)
    } finally {
      setLoading(false)
    }
  }, [table, select, filter, filterValue, orderBy, orderDirection, user])

  // Buscar dados iniciais
  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Configurar subscrição em tempo real
  useRealtimeSubscription({
    table,
    filter,
    filterValue,
    onEvent: (payload) => {
      if (payload.type === 'INSERT') {
        setData((currentData) => [...currentData, payload.data])
      } else if (payload.type === 'UPDATE') {
        setData((currentData) =>
          currentData.map((item: any) =>
            item.id === payload.data.id ? payload.data : item
          )
        )
      } else if (payload.type === 'DELETE') {
        setData((currentData) =>
          currentData.filter((item: any) => item.id !== payload.data.id)
        )
      }
    }
  })

  return {
    data,
    loading,
    error,
    refresh: fetchData
  }
}
```

### 3. Exemplo de Uso em um Componente

```tsx
// app/components/hiperfocos/ListaHiperfocos.tsx
import { useRealtimeData } from '../../hooks/useRealtimeData'

interface Hiperfoco {
  id: string
  titulo: string
  descricao: string
  cor: string
  data_inicio: string
  created_at: string
}

export function ListaHiperfocos() {
  const {
    data: hiperfocos,
    loading,
    error,
    refresh
  } = useRealtimeData<Hiperfoco>({
    table: 'hiperfoco_projetos',
    orderBy: 'created_at',
    orderDirection: 'desc'
  })

  if (loading) return <div>Carregando hiperfocos...</div>
  if (error) return <div>Erro ao carregar hiperfocos: {error}</div>

  return (
    <div className="lista-hiperfocos">
      <h2>Meus Hiperfocos</h2>
      <button onClick={refresh}>Atualizar</button>
      
      {hiperfocos.length === 0 ? (
        <p>Nenhum hiperfoco encontrado. Crie seu primeiro projeto!</p>
      ) : (
        <ul>
          {hiperfocos.map((hiperfoco) => (
            <li key={hiperfoco.id} style={{ borderLeft: `4px solid ${hiperfoco.cor}` }}>
              <h3>{hiperfoco.titulo}</h3>
              <p>{hiperfoco.descricao}</p>
              <small>Criado em: {new Date(hiperfoco.created_at).toLocaleDateString()}</small>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
```

## Implementação de Notificações em Tempo Real

Além da sincronização de dados, podemos usar o Realtime para implementar notificações em tempo real:

```typescript
// app/hooks/useNotifications.ts
import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase/client'
import { useAuth } from './useAuth'

interface Notification {
  id: string
  user_id: string
  title: string
  message: string
  read: boolean
  created_at: string
}

export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()

  // Buscar notificações
  useEffect(() => {
    if (!user) return

    const fetchNotifications = async () => {
      setLoading(true)

      const { data, error } = await supabase
        .from('notificacoes')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })

      if (error) {
        console.error('Erro ao buscar notificações:', error)
      } else {
        setNotifications(data || [])
        setUnreadCount(data?.filter(n => !n.read).length || 0)
      }

      setLoading(false)
    }

    fetchNotifications()

    // Subscrever a novas notificações
    const channel = supabase
      .channel(`public:notificacoes:user_id=eq.${user.id}`)
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'notificacoes',
        filter: `user_id=eq.${user.id}`
      }, (payload) => {
        const newNotification = payload.new as Notification
        
        // Adicionar à lista de notificações
        setNotifications(current => [newNotification, ...current])
        
        // Incrementar contador de não lidas
        setUnreadCount(count => count + 1)
        
        // Mostrar notificação no navegador
        if (Notification.permission === 'granted') {
          new Notification(newNotification.title, {
            body: newNotification.message
          })
        }
      })
      .on('postgres_changes', {
        event: 'UPDATE',
        schema: 'public',
        table: 'notificacoes',
        filter: `user_id=eq.${user.id}`
      }, (payload) => {
        const updatedNotification = payload.new as Notification
        
        // Atualizar na lista
        setNotifications(current => 
          current.map(n => n.id === updatedNotification.id ? updatedNotification : n)
        )
        
        // Atualizar contador de não lidas
        setUnreadCount(count => {
          const oldRead = (payload.old as Notification).read
          const newRead = updatedNotification.read
          
          if (!oldRead && newRead) return count - 1
          if (oldRead && !newRead) return count + 1
          return count
        })
      })
      .subscribe()

    // Solicitar permissão para notificações do navegador
    if (Notification.permission !== 'granted' && Notification.permission !== 'denied') {
      Notification.requestPermission()
    }

    return () => {
      supabase.removeChannel(channel)
    }
  }, [user])

  // Marcar notificação como lida
  const markAsRead = async (id: string) => {
    if (!user) return

    const { error } = await supabase
      .from('notificacoes')
      .update({ read: true })
      .eq('id', id)
      .eq('user_id', user.id)

    if (error) {
      console.error('Erro ao marcar notificação como lida:', error)
    }
  }

  // Marcar todas como lidas
  const markAllAsRead = async () => {
    if (!user) return

    const { error } = await supabase
      .from('notificacoes')
      .update({ read: true })
      .eq('user_id', user.id)
      .eq('read', false)

    if (error) {
      console.error('Erro ao marcar todas notificações como lidas:', error)
    } else {
      setNotifications(current => 
        current.map(n => ({ ...n, read: true }))
      )
      setUnreadCount(0)
    }
  }

  return {
    notifications,
    unreadCount,
    loading,
    markAsRead,
    markAllAsRead
  }
}
```

## Próximos Passos

Após a configuração do Realtime, os próximos passos são:

1. Implementar a sincronização em tempo real para todas as entidades principais
2. Configurar mecanismos de resolução de conflitos para edições simultâneas
3. Otimizar o desempenho das consultas em tempo real
4. Implementar testes de carga para verificar o comportamento com múltiplos clientes

A configuração adequada do Realtime é essencial para proporcionar uma experiência fluida aos usuários do StayFocus, permitindo que eles trabalhem em múltiplos dispositivos com sincronização instantânea de dados.
