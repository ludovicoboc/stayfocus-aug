# Implementação de Edge Functions

## Contexto

As Edge Functions do Supabase são funções serverless que permitem executar código personalizado em resposta a eventos ou chamadas HTTP. Elas são executadas na borda da rede, próximas aos usuários, o que resulta em menor latência e melhor desempenho. No contexto do StayFocus, as Edge Functions serão utilizadas para implementar lógicas de negócio complexas que não podem ser realizadas diretamente no cliente ou através de consultas SQL simples.

Conforme mencionado na documentação do projeto, uma das principais aplicações das Edge Functions será a integração com a assistente virtual Sati, que utilizará o modelo Sabiá 3 da Maritaca AI para fornecer suporte contextualizado aos usuários.

## Configuração Inicial

### 1. Instalação do Supabase CLI

Para desenvolver e implantar Edge Functions, é necessário instalar o Supabase CLI:

```bash
# Instalação via npm
npm install -g supabase

# Verificar instalação
supabase --version
```

### 2. Inicialização do Projeto Supabase Local

```bash
# Inicializar projeto Supabase local
supabase init
```

### 3. Configuração do Ambiente de Desenvolvimento

Crie um arquivo `.env.local` na raiz do projeto com as seguintes variáveis:

```bash
SUPABASE_URL=https://ngonttcfpjolvcszxgxk.supabase.co
SUPABASE_ANON_KEY=[SUA_CHAVE_ANON_KEY]
SUPABASE_SERVICE_ROLE_KEY=[SUA_CHAVE_SERVICE_ROLE]
MARITACA_API_KEY=[SUA_CHAVE_API_MARITACA]
```

## Implementação das Edge Functions

### 1. Função para Processamento de Lembretes

Esta função será responsável por verificar e enviar lembretes programados aos usuários:

```typescript
// supabase/functions/processar-lembretes/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Lidar com requisições OPTIONS (CORS preflight)
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Criar cliente Supabase
    const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Obter data e hora atual
    const agora = new Date()
    const diaSemana = agora.getDay() // 0 = Domingo, 1 = Segunda, ..., 6 = Sábado
    const horaAtual = agora.toTimeString().substring(0, 5) // Formato: "HH:MM"

    // Buscar lembretes ativos para o dia e hora atual
    const { data: lembretes, error } = await supabase
      .from('lembretes_sono')
      .select('id, user_id, horario, mensagem')
      .eq('ativo', true)
      .contains('dias_semana', [diaSemana])
      .eq('horario', horaAtual)

    if (error) {
      throw error
    }

    // Processar lembretes
    const resultados = []
    for (const lembrete of lembretes) {
      // Buscar informações do usuário
      const { data: usuario } = await supabase
        .from('user_profiles')
        .select('email, nome')
        .eq('id', lembrete.user_id)
        .single()

      if (usuario) {
        // Enviar notificação (implementação depende do método de notificação escolhido)
        // Exemplo: enviar e-mail
        const notificacaoEnviada = await enviarNotificacao(
          usuario.email,
          'Lembrete StayFocus',
          `Olá ${usuario.nome || 'usuário'}, ${lembrete.mensagem}`
        )

        resultados.push({
          lembrete_id: lembrete.id,
          usuario_id: lembrete.user_id,
          status: notificacaoEnviada ? 'enviado' : 'falha'
        })
      }
    }

    return new Response(
      JSON.stringify({ success: true, processados: resultados.length, resultados }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      }
    )
  }
})

// Função auxiliar para enviar notificações
async function enviarNotificacao(destinatario: string, assunto: string, mensagem: string): Promise<boolean> {
  // Implementação do envio de notificação
  // Pode ser via e-mail, push notification, etc.
  console.log(`Enviando notificação para ${destinatario}: ${assunto} - ${mensagem}`)
  
  // Simulação de envio bem-sucedido
  return true
}
```

### 2. Função para Integração com a Assistente Virtual Sati

Esta função será responsável por processar consultas à assistente virtual Sati, utilizando o modelo Sabiá 3 da Maritaca AI:

```typescript
// supabase/functions/sati-assistente/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Lidar com requisições OPTIONS (CORS preflight)
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Verificar se é uma requisição POST
    if (req.method !== 'POST') {
      throw new Error('Método não permitido')
    }

    // Obter dados da requisição
    const { consulta, userId } = await req.json()

    if (!consulta) {
      throw new Error('Consulta não fornecida')
    }

    // Criar cliente Supabase
    const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Verificar autenticação
    if (userId) {
      // Buscar contexto do usuário para personalizar a resposta
      const { data: userContext } = await supabase
        .from('user_profiles')
        .select('nome')
        .eq('id', userId)
        .single()

      // Registrar consulta no histórico
      await supabase
        .from('historico_consultas_sati')
        .insert({
          user_id: userId,
          consulta,
          timestamp: new Date().toISOString()
        })
    }

    // Chamar a API da Maritaca AI
    const maritacaApiKey = Deno.env.get('MARITACA_API_KEY')
    if (!maritacaApiKey) {
      throw new Error('Chave de API da Maritaca não configurada')
    }

    const resposta = await consultarMaritacaAI(consulta, maritacaApiKey)

    // Registrar resposta no histórico se houver usuário autenticado
    if (userId) {
      await supabase
        .from('historico_consultas_sati')
        .update({
          resposta: resposta.texto,
          tokens_utilizados: resposta.tokens
        })
        .eq('user_id', userId)
        .eq('consulta', consulta)
        .is('resposta', null)
    }

    return new Response(
      JSON.stringify({ success: true, resposta: resposta.texto }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      }
    )
  }
})

// Função para consultar a API da Maritaca AI
async function consultarMaritacaAI(consulta: string, apiKey: string): Promise<{ texto: string, tokens: number }> {
  try {
    const response = await fetch('https://api.maritaca.ai/api/v1/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: 'sabia-3',
        prompt: consulta,
        temperature: 0.7,
        max_tokens: 1024,
        top_p: 0.9
      })
    })

    if (!response.ok) {
      throw new Error(`Erro na API da Maritaca: ${response.statusText}`)
    }

    const data = await response.json()
    return {
      texto: data.response,
      tokens: data.usage.total_tokens
    }
  } catch (error) {
    console.error('Erro ao consultar Maritaca AI:', error)
    return {
      texto: 'Desculpe, não consegui processar sua consulta no momento. Por favor, tente novamente mais tarde.',
      tokens: 0
    }
  }
}
```

### 3. Função para Sincronização de Dados Offline

Esta função será responsável por sincronizar dados que foram modificados offline quando o usuário voltar a ficar online:

```typescript
// supabase/functions/sincronizar-dados-offline/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Lidar com requisições OPTIONS (CORS preflight)
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Verificar se é uma requisição POST
    if (req.method !== 'POST') {
      throw new Error('Método não permitido')
    }

    // Obter dados da requisição
    const { userId, dadosOffline } = await req.json()

    if (!userId || !dadosOffline) {
      throw new Error('Dados incompletos')
    }

    // Criar cliente Supabase
    const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Processar cada tipo de dado
    const resultados = {}

    // Processar tarefas
    if (dadosOffline.tarefas && dadosOffline.tarefas.length > 0) {
      resultados.tarefas = await processarTarefas(supabase, userId, dadosOffline.tarefas)
    }

    // Processar notas
    if (dadosOffline.notas && dadosOffline.notas.length > 0) {
      resultados.notas = await processarNotas(supabase, userId, dadosOffline.notas)
    }

    // Processar outros tipos de dados conforme necessário...

    return new Response(
      JSON.stringify({ success: true, resultados }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      }
    )
  }
})

// Função para processar tarefas offline
async function processarTarefas(supabase, userId, tarefas) {
  const resultados = {
    inseridas: 0,
    atualizadas: 0,
    erros: 0
  }

  for (const tarefa of tarefas) {
    try {
      // Verificar se a tarefa já existe
      const { data: tarefaExistente } = await supabase
        .from('tarefas')
        .select('id, updated_at')
        .eq('id', tarefa.id)
        .single()

      if (!tarefaExistente) {
        // Inserir nova tarefa
        await supabase
          .from('tarefas')
          .insert({
            ...tarefa,
            user_id: userId,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          })
        resultados.inseridas++
      } else {
        // Verificar timestamp para evitar sobrescrever dados mais recentes
        const tarefaTimestamp = new Date(tarefa.updated_at).getTime()
        const dbTimestamp = new Date(tarefaExistente.updated_at).getTime()

        if (tarefaTimestamp > dbTimestamp) {
          // Atualizar tarefa existente
          await supabase
            .from('tarefas')
            .update({
              ...tarefa,
              updated_at: new Date().toISOString()
            })
            .eq('id', tarefa.id)
          resultados.atualizadas++
        }
      }
    } catch (error) {
      console.error('Erro ao processar tarefa:', error)
      resultados.erros++
    }
  }

  return resultados
}

// Função para processar notas offline
async function processarNotas(supabase, userId, notas) {
  // Implementação similar à função processarTarefas
  // ...
  return { inseridas: 0, atualizadas: 0, erros: 0 }
}
```

## Implantação das Edge Functions

Para implantar as Edge Functions no Supabase, siga os passos abaixo:

### 1. Autenticação com o Supabase CLI

```bash
supabase login
```

### 2. Vinculação ao Projeto Supabase

```bash
supabase link --project-ref ngonttcfpjolvcszxgxk
```

### 3. Implantação das Funções

```bash
supabase functions deploy processar-lembretes
supabase functions deploy sati-assistente
supabase functions deploy sincronizar-dados-offline
```

### 4. Configuração de Segredos

```bash
supabase secrets set MARITACA_API_KEY=sua_chave_api_maritaca
```

## Integração com o Frontend

### 1. Hook para Chamada de Edge Functions

```typescript
// app/hooks/useEdgeFunctions.ts
import { useState } from 'react'
import { supabase } from '../lib/supabase/client'

export function useEdgeFunctions() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Função para consultar a assistente Sati
  const consultarSati = async (consulta: string) => {
    try {
      setLoading(true)
      setError(null)

      const { data: user } = await supabase.auth.getUser()
      const userId = user?.user?.id

      const { data, error } = await supabase.functions.invoke('sati-assistente', {
        body: { consulta, userId }
      })

      if (error) {
        throw error
      }

      return { data }
    } catch (err: any) {
      setError(err.message || 'Erro ao consultar a assistente Sati')
      return { error: err }
    } finally {
      setLoading(false)
    }
  }

  // Função para sincronizar dados offline
  const sincronizarDadosOffline = async (dadosOffline: any) => {
    try {
      setLoading(true)
      setError(null)

      const { data: user } = await supabase.auth.getUser()
      const userId = user?.user?.id

      if (!userId) {
        throw new Error('Usuário não autenticado')
      }

      const { data, error } = await supabase.functions.invoke('sincronizar-dados-offline', {
        body: { userId, dadosOffline }
      })

      if (error) {
        throw error
      }

      return { data }
    } catch (err: any) {
      setError(err.message || 'Erro ao sincronizar dados offline')
      return { error: err }
    } finally {
      setLoading(false)
    }
  }

  return {
    loading,
    error,
    consultarSati,
    sincronizarDadosOffline
  }
}
```

## Próximos Passos

Após a implementação das Edge Functions, os próximos passos são:

1. Implementar a integração completa com o frontend
2. Configurar a sincronização em tempo real
3. Implementar mecanismos de cache local para funcionamento offline
4. Realizar testes de carga e otimização

As Edge Functions são uma parte essencial da arquitetura do StayFocus, permitindo a implementação de lógicas de negócio complexas e a integração com serviços externos como a Maritaca AI para a assistente virtual Sati.
