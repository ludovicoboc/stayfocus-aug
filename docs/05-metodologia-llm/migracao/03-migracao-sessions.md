# Migração Sessions Store

## Objetivo
Migrar o sistema de sessões Pomodoro do localStorage para Supabase, mantendo histórico e estatísticas.

## Pré-requisitos
- ✅ Configuração inicial do Supabase completa
- ✅ Schema da tabela `pomodoro_sessions` criado
- ✅ RLS configurado
- ✅ Backup do localStorage realizado

## Estrutura da Tabela Sessions

```sql
CREATE TABLE pomodoro_sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
  session_type VARCHAR(20) NOT NULL, -- 'focus', 'short_break', 'long_break'
  duration INTEGER NOT NULL, -- duração em segundos
  completed BOOLEAN DEFAULT false,
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ended_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  notes TEXT,
  interruptions INTEGER DEFAULT 0,
  productivity_score INTEGER CHECK (productivity_score >= 1 AND productivity_score <= 5)
);

-- Índices para performance
CREATE INDEX idx_pomodoro_sessions_user_id ON pomodoro_sessions(user_id);
CREATE INDEX idx_pomodoro_sessions_task_id ON pomodoro_sessions(task_id);
CREATE INDEX idx_pomodoro_sessions_date ON pomodoro_sessions(started_at);
```

## Etapas de Migração

### 1. Análise dos Dados Existentes
```typescript
// Verificar estrutura atual no localStorage
const currentSessions = localStorage.getItem('stayfocus_sessions');
const sessionsData = JSON.parse(currentSessions || '[]');

console.log('Total de sessões:', sessionsData.length);
console.log('Tipos de sessão:', [...new Set(sessionsData.map(s => s.type))]);
console.log('Período de dados:', {
  inicio: Math.min(...sessionsData.map(s => new Date(s.startTime).getTime())),
  fim: Math.max(...sessionsData.map(s => new Date(s.endTime || Date.now()).getTime()))
});
```

### 2. Criação do Service de Sessions
```typescript
// src/services/sessionsService.ts
import { supabase } from './supabaseClient';

export class SessionsService {
  async getSessions(userId: string, filters?: {
    startDate?: Date;
    endDate?: Date;
    taskId?: string;
    sessionType?: string;
  }) {
    let query = supabase
      .from('pomodoro_sessions')
      .select(`
        *,
        tasks:task_id (
          id,
          title,
          category
        )
      `)
      .eq('user_id', userId)
      .order('started_at', { ascending: false });

    if (filters?.startDate) {
      query = query.gte('started_at', filters.startDate.toISOString());
    }
    
    if (filters?.endDate) {
      query = query.lte('started_at', filters.endDate.toISOString());
    }

    if (filters?.taskId) {
      query = query.eq('task_id', filters.taskId);
    }

    if (filters?.sessionType) {
      query = query.eq('session_type', filters.sessionType);
    }

    const { data, error } = await query;
    
    if (error) throw error;
    return data;
  }

  async startSession(sessionData: {
    taskId?: string;
    sessionType: string;
    duration: number;
  }) {
    const { data, error } = await supabase
      .from('pomodoro_sessions')
      .insert([{
        ...sessionData,
        user_id: await getCurrentUserId(),
        started_at: new Date().toISOString()
      }])
      .select()
      .single();
    
    if (error) throw error;
    return data;
  }

  async completeSession(id: string, data: {
    completed: boolean;
    endedAt: Date;
    notes?: string;
    interruptions?: number;
    productivityScore?: number;
  }) {
    const { data: session, error } = await supabase
      .from('pomodoro_sessions')
      .update({
        completed: data.completed,
        ended_at: data.endedAt.toISOString(),
        notes: data.notes,
        interruptions: data.interruptions,
        productivity_score: data.productivityScore
      })
      .eq('id', id)
      .select()
      .single();
    
    if (error) throw error;
    return session;
  }

  async getStatistics(userId: string, period: 'day' | 'week' | 'month' | 'year') {
    const { data, error } = await supabase
      .rpc('get_pomodoro_statistics', {
        user_id: userId,
        period_type: period
      });
    
    if (error) throw error;
    return data;
  }
}
```

### 3. Criação de Funções SQL para Estatísticas
```sql
-- Função para calcular estatísticas de produtividade
CREATE OR REPLACE FUNCTION get_pomodoro_statistics(
  user_id UUID,
  period_type TEXT DEFAULT 'week'
)
RETURNS JSON AS $$
DECLARE
  start_date TIMESTAMP;
  result JSON;
BEGIN
  -- Definir período
  CASE period_type
    WHEN 'day' THEN start_date := CURRENT_DATE;
    WHEN 'week' THEN start_date := DATE_TRUNC('week', CURRENT_DATE);
    WHEN 'month' THEN start_date := DATE_TRUNC('month', CURRENT_DATE);
    WHEN 'year' THEN start_date := DATE_TRUNC('year', CURRENT_DATE);
    ELSE start_date := DATE_TRUNC('week', CURRENT_DATE);
  END CASE;

  -- Calcular estatísticas
  SELECT JSON_BUILD_OBJECT(
    'total_sessions', COUNT(*),
    'completed_sessions', COUNT(*) FILTER (WHERE completed = true),
    'focus_time', SUM(duration) FILTER (WHERE session_type = 'focus' AND completed = true),
    'break_time', SUM(duration) FILTER (WHERE session_type IN ('short_break', 'long_break') AND completed = true),
    'average_productivity', AVG(productivity_score) FILTER (WHERE productivity_score IS NOT NULL),
    'total_interruptions', SUM(interruptions),
    'sessions_by_type', JSON_BUILD_OBJECT(
      'focus', COUNT(*) FILTER (WHERE session_type = 'focus'),
      'short_break', COUNT(*) FILTER (WHERE session_type = 'short_break'),
      'long_break', COUNT(*) FILTER (WHERE session_type = 'long_break')
    ),
    'daily_breakdown', (
      SELECT JSON_AGG(
        JSON_BUILD_OBJECT(
          'date', DATE(started_at),
          'sessions', COUNT(*),
          'focus_time', SUM(duration) FILTER (WHERE session_type = 'focus' AND completed = true)
        )
      )
      FROM pomodoro_sessions
      WHERE user_id = get_pomodoro_statistics.user_id
        AND started_at >= start_date
      GROUP BY DATE(started_at)
      ORDER BY DATE(started_at)
    )
  ) INTO result
  FROM pomodoro_sessions
  WHERE pomodoro_sessions.user_id = get_pomodoro_statistics.user_id
    AND started_at >= start_date;

  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 4. Migração dos Dados
```typescript
async function migrateSessions() {
  try {
    // 1. Ler dados do localStorage
    const localSessions = JSON.parse(localStorage.getItem('stayfocus_sessions') || '[]');
    console.log(`Migrando ${localSessions.length} sessões...`);

    // 2. Transformar dados para formato Supabase
    const transformedSessions = localSessions.map(session => ({
      user_id: getCurrentUserId(),
      task_id: session.taskId || null,
      session_type: session.type || 'focus',
      duration: session.duration || 1500, // 25 minutos padrão
      completed: session.completed || false,
      started_at: session.startTime || new Date().toISOString(),
      ended_at: session.endTime || null,
      notes: session.notes || null,
      interruptions: session.interruptions || 0,
      productivity_score: session.productivityScore || null
    }));

    // 3. Validar dados antes da migração
    const invalidSessions = transformedSessions.filter(session => 
      !session.session_type || !session.duration
    );
    
    if (invalidSessions.length > 0) {
      console.warn('Sessões inválidas encontradas:', invalidSessions);
    }

    // 4. Inserir em lotes
    const batchSize = 50;
    const validSessions = transformedSessions.filter(session => 
      session.session_type && session.duration
    );

    for (let i = 0; i < validSessions.length; i += batchSize) {
      const batch = validSessions.slice(i, i + batchSize);
      
      const { error } = await supabase
        .from('pomodoro_sessions')
        .insert(batch);
      
      if (error) {
        console.error(`Erro no lote ${i / batchSize + 1}:`, error);
        throw error;
      }
      
      console.log(`Lote ${i / batchSize + 1}/${Math.ceil(validSessions.length / batchSize)} migrado`);
    }

    console.log('✅ Migração de sessões concluída com sucesso');
    return { migrated: validSessions.length, skipped: invalidSessions.length };
  } catch (error) {
    console.error('❌ Erro na migração de sessões:', error);
    throw error;
  }
}
```

### 5. Atualização dos Hooks
```typescript
// src/hooks/usePomodoroSessions.ts
import { useState, useEffect } from 'react';
import { SessionsService } from '../services/sessionsService';

export function usePomodoroSessions() {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const sessionsService = new SessionsService();

  const loadSessions = async (filters?) => {
    try {
      setLoading(true);
      const userId = await getCurrentUserId();
      const data = await sessionsService.getSessions(userId, filters);
      setSessions(data);
    } catch (error) {
      console.error('Erro ao carregar sessões:', error);
    } finally {
      setLoading(false);
    }
  };

  const startSession = async (sessionData) => {
    try {
      const newSession = await sessionsService.startSession(sessionData);
      setCurrentSession(newSession);
      return newSession;
    } catch (error) {
      console.error('Erro ao iniciar sessão:', error);
      throw error;
    }
  };

  const completeSession = async (sessionId, completionData) => {
    try {
      const updatedSession = await sessionsService.completeSession(sessionId, completionData);
      setSessions(prev => prev.map(s => s.id === sessionId ? updatedSession : s));
      setCurrentSession(null);
      return updatedSession;
    } catch (error) {
      console.error('Erro ao completar sessão:', error);
      throw error;
    }
  };

  const loadStatistics = async (period = 'week') => {
    try {
      const userId = await getCurrentUserId();
      const stats = await sessionsService.getStatistics(userId, period);
      setStatistics(stats);
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  useEffect(() => {
    loadSessions();
    loadStatistics();
  }, []);

  return {
    sessions,
    currentSession,
    statistics,
    loading,
    startSession,
    completeSession,
    loadSessions,
    loadStatistics
  };
}
```

## Validação e Testes

### 1. Validação de Integridade
```typescript
async function validateSessionsMigration() {
  const localSessions = JSON.parse(localStorage.getItem('stayfocus_sessions') || '[]');
  const { data: supabaseSessions } = await supabase
    .from('pomodoro_sessions')
    .select('*')
    .eq('user_id', userId);

  console.log('Sessões locais:', localSessions.length);
  console.log('Sessões no Supabase:', supabaseSessions.length);

  // Verificar estatísticas básicas
  const localCompleted = localSessions.filter(s => s.completed).length;
  const supabaseCompleted = supabaseSessions.filter(s => s.completed).length;

  if (Math.abs(localCompleted - supabaseCompleted) > 5) {
    throw new Error('Discrepância significativa nas sessões completadas');
  }

  console.log('✅ Validação de sessões bem-sucedida');
}
```

### 2. Teste de Performance de Estatísticas
```typescript
async function testStatisticsPerformance() {
  const startTime = Date.now();
  
  await sessionsService.getStatistics(userId, 'month');
  
  const executionTime = Date.now() - startTime;
  console.log(`Tempo de execução das estatísticas: ${executionTime}ms`);
  
  if (executionTime > 2000) {
    console.warn('⚠️ Consulta de estatísticas lenta');
  }
}
```

## Checklist de Validação
- [ ] Sessões migradas corretamente
- [ ] Estatísticas funcionando
- [ ] Performance adequada (< 2s para estatísticas)
- [ ] Associações com tasks mantidas
- [ ] Histórico preservado
- [ ] Funções SQL criadas
- [ ] Índices otimizados
- [ ] Backup mantido
