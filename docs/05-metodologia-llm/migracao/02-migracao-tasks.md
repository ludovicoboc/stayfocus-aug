# Migração Tasks Store

## Objetivo
Migrar o sistema de gerenciamento de tarefas do localStorage para Supabase, mantendo todas as funcionalidades existentes.

## Pré-requisitos
- ✅ Configuração inicial do Supabase completa
- ✅ Schema da tabela `tasks` criado
- ✅ RLS configurado
- ✅ Backup do localStorage realizado

## Estrutura da Tabela Tasks

```sql
CREATE TABLE tasks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  category VARCHAR(50),
  priority VARCHAR(20) DEFAULT 'medium',
  status VARCHAR(20) DEFAULT 'pending',
  due_date TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  tags TEXT[],
  estimated_duration INTEGER, -- em minutos
  actual_duration INTEGER,
  completed_at TIMESTAMP WITH TIME ZONE
);
```

## Etapas de Migração

### 1. Análise dos Dados Existentes
```typescript
// Verificar estrutura atual no localStorage
const currentTasks = localStorage.getItem('stayfocus_tasks');
console.log('Estrutura atual:', JSON.parse(currentTasks || '[]'));

// Validar campos obrigatórios
const tasks = JSON.parse(currentTasks || '[]');
const validationErrors = tasks.filter(task => !task.title || !task.id);
console.log('Erros de validação:', validationErrors);
```

### 2. Criação do Service de Tasks
```typescript
// src/services/tasksService.ts
import { supabase } from './supabaseClient';

export class TasksService {
  async getTasks(userId: string) {
    const { data, error } = await supabase
      .from('tasks')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });
    
    if (error) throw error;
    return data;
  }

  async createTask(task: Omit<Task, 'id' | 'created_at' | 'updated_at'>) {
    const { data, error } = await supabase
      .from('tasks')
      .insert([task])
      .select()
      .single();
    
    if (error) throw error;
    return data;
  }

  async updateTask(id: string, updates: Partial<Task>) {
    const { data, error } = await supabase
      .from('tasks')
      .update({ ...updates, updated_at: new Date().toISOString() })
      .eq('id', id)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  }

  async deleteTask(id: string) {
    const { error } = await supabase
      .from('tasks')
      .delete()
      .eq('id', id);
    
    if (error) throw error;
  }
}
```

### 3. Migração dos Dados
```typescript
async function migrateTasks() {
  try {
    // 1. Ler dados do localStorage
    const localTasks = JSON.parse(localStorage.getItem('stayfocus_tasks') || '[]');
    
    // 2. Transformar dados para formato Supabase
    const transformedTasks = localTasks.map(task => ({
      ...task,
      user_id: await getCurrentUserId(),
      created_at: task.createdAt || new Date().toISOString(),
      updated_at: task.updatedAt || new Date().toISOString()
    }));

    // 3. Inserir em lotes
    const batchSize = 100;
    for (let i = 0; i < transformedTasks.length; i += batchSize) {
      const batch = transformedTasks.slice(i, i + batchSize);
      
      const { error } = await supabase
        .from('tasks')
        .insert(batch);
      
      if (error) throw error;
      console.log(`Lote ${i / batchSize + 1} migrado com sucesso`);
    }

    console.log('Migração de tasks concluída com sucesso');
  } catch (error) {
    console.error('Erro na migração:', error);
    throw error;
  }
}
```

### 4. Atualização dos Stores/Hooks
```typescript
// src/hooks/useTasks.ts
import { useState, useEffect } from 'react';
import { TasksService } from '../services/tasksService';

export function useTasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const tasksService = new TasksService();

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const userId = await getCurrentUserId();
      const data = await tasksService.getTasks(userId);
      setTasks(data);
    } catch (error) {
      console.error('Erro ao carregar tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const createTask = async (taskData) => {
    try {
      const newTask = await tasksService.createTask(taskData);
      setTasks(prev => [newTask, ...prev]);
      return newTask;
    } catch (error) {
      console.error('Erro ao criar task:', error);
      throw error;
    }
  };

  return {
    tasks,
    loading,
    createTask,
    updateTask,
    deleteTask,
    refreshTasks: loadTasks
  };
}
```

## Validação e Testes

### 1. Testes de Integridade
```typescript
async function validateTasksMigration() {
  const localTasks = JSON.parse(localStorage.getItem('stayfocus_tasks') || '[]');
  const { data: supabaseTasks } = await supabase
    .from('tasks')
    .select('*')
    .eq('user_id', userId);

  // Verificar quantidade
  if (localTasks.length !== supabaseTasks.length) {
    throw new Error('Quantidade de tasks não confere');
  }

  // Verificar dados críticos
  for (const localTask of localTasks) {
    const supabaseTask = supabaseTasks.find(t => t.title === localTask.title);
    if (!supabaseTask) {
      throw new Error(`Task não encontrada: ${localTask.title}`);
    }
  }

  console.log('✅ Validação de tasks bem-sucedida');
}
```

### 2. Testes de Performance
```typescript
async function testTasksPerformance() {
  const startTime = Date.now();
  
  // Teste de carregamento
  await tasksService.getTasks(userId);
  const loadTime = Date.now() - startTime;
  
  console.log(`Tempo de carregamento: ${loadTime}ms`);
  
  if (loadTime > 1000) {
    console.warn('⚠️ Carregamento lento detectado');
  }
}
```

## Rollback
Se necessário, os dados podem ser restaurados do backup:
```typescript
function rollbackTasks() {
  const backup = localStorage.getItem('stayfocus_tasks_backup');
  if (backup) {
    localStorage.setItem('stayfocus_tasks', backup);
    console.log('Rollback realizado com sucesso');
  }
}
```

## Checklist de Validação
- [ ] Todos os dados migrados corretamente
- [ ] Funcionalidades CRUD funcionando
- [ ] Performance adequada (< 1s para carregamento)
- [ ] RLS funcionando corretamente
- [ ] Sincronização em tempo real ativa
- [ ] Backup local mantido por 30 dias
- [ ] Logs de migração salvos
