# 05 - Implementação da Assistente SATI

## 🤖 Visão Geral da SATI

### Definição:
**SATI** (Sistema de Assistência Técnica Inteligente) é uma assistente virtual baseada em IA que utiliza o modelo Sabiá 3 da Maritaca AI com tecnologia RAG (Retrieval Augmented Generation) para fornecer suporte contextualizado aos usuários do StayFocus.

### Objetivos:
1. **Assistência contextual** baseada nos dados do usuário
2. **Respostas personalizadas** usando RAG
3. **Interface conversacional** web e WhatsApp
4. **Aprendizado contínuo** com feedback do usuário

## 🏗️ Arquitetura da SATI

### Componentes Principais:
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Interface     │    │   SATI Core     │    │   Maritaca AI   │
│  (Web/WhatsApp) │◄──►│    Service      │◄──►│   (Sabiá 3)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   RAG System    │
                       │  (Embeddings)   │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Supabase      │
                       │  (User Data)    │
                       └─────────────────┘
```

## 📋 FASE 1: Configuração Base da SATI

### 1.1 **Setup da Integração Maritaca AI**

#### A. Configuração do Cliente
```typescript
// lib/sati/maritacaClient.ts
interface MaritacaResponse {
  id: string
  choices: Array<{
    message: {
      role: 'assistant' | 'user' | 'system'
      content: string
    }
    finish_reason: string
  }>
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

export class MaritacaClient {
  private apiKey: string
  private baseUrl: string = 'https://chat.maritaca.ai/api'

  constructor(apiKey: string) {
    this.apiKey = apiKey
  }

  async completion(messages: any[], options: any = {}): Promise<MaritacaResponse> {
    const response = await fetch(`${this.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'sabia-3',
        messages,
        temperature: options.temperature || 0.7,
        max_tokens: options.max_tokens || 1000,
        ...options
      })
    })

    if (!response.ok) {
      throw new Error(`Maritaca API error: ${response.statusText}`)
    }

    return response.json()
  }

  async generateEmbedding(text: string): Promise<number[]> {
    const response = await fetch(`${this.baseUrl}/embeddings`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'text-embedding-ada-002', // Verificar modelo correto
        input: text
      })
    })

    if (!response.ok) {
      throw new Error(`Maritaca Embedding API error: ${response.statusText}`)
    }

    const data = await response.json()
    return data.data[0].embedding
  }
}
```

#### B. Configuração de Ambiente
```typescript
// .env.local - Adicionar
MARITACA_API_KEY=your_maritaca_api_key_here
NEXT_PUBLIC_SATI_ENABLED=true
```

### 1.2 **Schema do Banco para SATI**

#### A. Tabelas Necessárias
```sql
-- Conversas da SATI
CREATE TABLE sati_conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  title TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Mensagens das conversas
CREATE TABLE sati_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID REFERENCES sati_conversations(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Base de conhecimento para RAG
CREATE TABLE sati_knowledge_base (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  embedding vector(1536), -- Ajustar dimensão conforme modelo
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Índice para busca vetorial
CREATE INDEX ON sati_knowledge_base USING ivfflat (embedding vector_cosine_ops);

-- RLS
ALTER TABLE sati_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE sati_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE sati_knowledge_base ENABLE ROW LEVEL SECURITY;

-- Políticas
CREATE POLICY "Users can manage own conversations" ON sati_conversations
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own messages" ON sati_messages
    FOR ALL USING (auth.uid() = (
        SELECT user_id FROM sati_conversations WHERE id = conversation_id
    ));

CREATE POLICY "Users can manage own knowledge" ON sati_knowledge_base
    FOR ALL USING (auth.uid() = user_id);
```

### 1.3 **Tipos TypeScript para SATI**

```typescript
// lib/sati/types.ts
export interface SatiConversation {
  id: string
  user_id: string
  title: string | null
  created_at: string
  updated_at: string
}

export interface SatiMessage {
  id: string
  conversation_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata: Record<string, any>
  created_at: string
}

export interface SatiKnowledgeItem {
  id: string
  user_id: string
  content: string
  metadata: Record<string, any>
  embedding: number[]
  created_at: string
  updated_at: string
}

export interface SatiContext {
  userPreferences: any
  recentActivity: any[]
  currentGoals: any[]
  relevantData: any[]
}

export interface SatiRequest {
  message: string
  conversationId?: string
  context?: Partial<SatiContext>
}

export interface SatiResponse {
  message: string
  conversationId: string
  messageId: string
  suggestions?: string[]
  actions?: Array<{
    type: string
    label: string
    data: any
  }>
}
```

## 📋 FASE 2: Sistema RAG (Retrieval Augmented Generation)

### 2.1 **Serviço de Embeddings**

#### A. Geração de Embeddings
```typescript
// lib/sati/embeddingService.ts
import { MaritacaClient } from './maritacaClient'
import { supabase } from '../supabase/client'

export class EmbeddingService {
  private maritaca: MaritacaClient

  constructor(apiKey: string) {
    this.maritaca = new MaritacaClient(apiKey)
  }

  async generateEmbedding(text: string): Promise<number[]> {
    try {
      return await this.maritaca.generateEmbedding(text)
    } catch (error) {
      console.error('Error generating embedding:', error)
      throw error
    }
  }

  async indexUserData(userId: string): Promise<void> {
    // Coletar dados do usuário de diferentes tabelas
    const userData = await this.collectUserData(userId)
    
    for (const data of userData) {
      const embedding = await this.generateEmbedding(data.content)
      
      await supabase
        .from('sati_knowledge_base')
        .upsert({
          user_id: userId,
          content: data.content,
          metadata: data.metadata,
          embedding: embedding,
          updated_at: new Date().toISOString()
        })
    }
  }

  private async collectUserData(userId: string) {
    const data = []

    // Coletar dados de diferentes fontes
    // Notas de autoconhecimento
    const { data: notas } = await supabase
      .from('notas_autoconhecimento')
      .select('*')
      .eq('user_id', userId)

    if (notas) {
      notas.forEach(nota => {
        data.push({
          content: `Nota de ${nota.categoria}: ${nota.titulo}. ${nota.conteudo}`,
          metadata: {
            type: 'nota_autoconhecimento',
            categoria: nota.categoria,
            id: nota.id
          }
        })
      })
    }

    // Adicionar outros tipos de dados...
    // Refeições, estudos, etc.

    return data
  }

  async searchSimilar(query: string, userId: string, limit: number = 5): Promise<any[]> {
    const queryEmbedding = await this.generateEmbedding(query)
    
    const { data, error } = await supabase
      .rpc('match_documents', {
        query_embedding: queryEmbedding,
        match_threshold: 0.7,
        match_count: limit,
        user_id: userId
      })

    if (error) throw error
    return data
  }
}
```

#### B. Função SQL para Busca Vetorial
```sql
-- Função para busca de similaridade
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding vector(1536),
  match_threshold float,
  match_count int,
  user_id uuid
)
RETURNS TABLE (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE SQL STABLE
AS $$
  SELECT
    id,
    content,
    metadata,
    1 - (embedding <=> query_embedding) as similarity
  FROM sati_knowledge_base
  WHERE 
    sati_knowledge_base.user_id = match_documents.user_id
    AND 1 - (embedding <=> query_embedding) > match_threshold
  ORDER BY embedding <=> query_embedding
  LIMIT match_count;
$$;
```

### 2.2 **Serviço de Contexto**

```typescript
// lib/sati/contextService.ts
import { supabase } from '../supabase/client'
import { EmbeddingService } from './embeddingService'

export class ContextService {
  private embeddingService: EmbeddingService

  constructor(embeddingService: EmbeddingService) {
    this.embeddingService = embeddingService
  }

  async buildContext(userId: string, query: string): Promise<SatiContext> {
    // Buscar dados relevantes usando RAG
    const relevantData = await this.embeddingService.searchSimilar(query, userId)
    
    // Buscar dados recentes
    const recentActivity = await this.getRecentActivity(userId)
    
    // Buscar preferências
    const userPreferences = await this.getUserPreferences(userId)
    
    // Buscar metas atuais
    const currentGoals = await this.getCurrentGoals(userId)

    return {
      userPreferences,
      recentActivity,
      currentGoals,
      relevantData
    }
  }

  private async getRecentActivity(userId: string) {
    // Implementar busca de atividades recentes
    // Últimas refeições, estudos, etc.
    return []
  }

  private async getUserPreferences(userId: string) {
    const { data } = await supabase
      .from('user_preferences')
      .select('*')
      .eq('user_id', userId)
      .single()
    
    return data
  }

  private async getCurrentGoals(userId: string) {
    // Implementar busca de metas atuais
    return []
  }
}
```

## 📋 FASE 3: Core Service da SATI

### 3.1 **Serviço Principal**

```typescript
// lib/sati/satiService.ts
import { MaritacaClient } from './maritacaClient'
import { ContextService } from './contextService'
import { EmbeddingService } from './embeddingService'
import { supabase } from '../supabase/client'

export class SatiService {
  private maritaca: MaritacaClient
  private contextService: ContextService
  private embeddingService: EmbeddingService

  constructor(apiKey: string) {
    this.maritaca = new MaritacaClient(apiKey)
    this.embeddingService = new EmbeddingService(apiKey)
    this.contextService = new ContextService(this.embeddingService)
  }

  async processMessage(request: SatiRequest, userId: string): Promise<SatiResponse> {
    try {
      // 1. Criar ou recuperar conversa
      const conversationId = request.conversationId || await this.createConversation(userId)
      
      // 2. Salvar mensagem do usuário
      const userMessage = await this.saveMessage(conversationId, 'user', request.message)
      
      // 3. Construir contexto usando RAG
      const context = await this.contextService.buildContext(userId, request.message)
      
      // 4. Construir prompt com contexto
      const messages = await this.buildPrompt(conversationId, request.message, context)
      
      // 5. Gerar resposta com Maritaca
      const response = await this.maritaca.completion(messages)
      
      // 6. Salvar resposta da assistente
      const assistantMessage = await this.saveMessage(
        conversationId, 
        'assistant', 
        response.choices[0].message.content
      )
      
      // 7. Gerar sugestões e ações
      const suggestions = await this.generateSuggestions(context, request.message)
      const actions = await this.generateActions(context, request.message)
      
      return {
        message: response.choices[0].message.content,
        conversationId,
        messageId: assistantMessage.id,
        suggestions,
        actions
      }
      
    } catch (error) {
      console.error('Error processing SATI message:', error)
      throw error
    }
  }

  private async createConversation(userId: string): Promise<string> {
    const { data, error } = await supabase
      .from('sati_conversations')
      .insert({
        user_id: userId,
        title: 'Nova Conversa'
      })
      .select()
      .single()

    if (error) throw error
    return data.id
  }

  private async saveMessage(conversationId: string, role: string, content: string) {
    const { data, error } = await supabase
      .from('sati_messages')
      .insert({
        conversation_id: conversationId,
        role,
        content
      })
      .select()
      .single()

    if (error) throw error
    return data
  }

  private async buildPrompt(conversationId: string, currentMessage: string, context: SatiContext) {
    // Buscar histórico da conversa
    const { data: history } = await supabase
      .from('sati_messages')
      .select('*')
      .eq('conversation_id', conversationId)
      .order('created_at', { ascending: true })
      .limit(10)

    const messages = []

    // System prompt
    messages.push({
      role: 'system',
      content: this.buildSystemPrompt(context)
    })

    // Histórico da conversa
    if (history) {
      history.forEach(msg => {
        messages.push({
          role: msg.role,
          content: msg.content
        })
      })
    }

    // Mensagem atual com contexto
    messages.push({
      role: 'user',
      content: `${currentMessage}\n\nContexto relevante: ${JSON.stringify(context.relevantData, null, 2)}`
    })

    return messages
  }

  private buildSystemPrompt(context: SatiContext): string {
    return `
Você é a SATI, assistente virtual do StayFocus, especializada em produtividade e bem-estar.

CONTEXTO DO USUÁRIO:
- Preferências: ${JSON.stringify(context.userPreferences)}
- Atividades recentes: ${JSON.stringify(context.recentActivity)}
- Metas atuais: ${JSON.stringify(context.currentGoals)}

DIRETRIZES:
1. Seja sempre empática e positiva
2. Use dados do contexto para personalizar respostas
3. Ofereça sugestões práticas e acionáveis
4. Mantenha foco em produtividade e bem-estar
5. Seja concisa mas completa
6. Use linguagem natural e amigável

ESPECIALIDADES:
- Técnicas de estudo e concentração
- Gestão de tempo e Pomodoro
- Alimentação e hidratação
- Sono e descanso
- Autoconhecimento
- Preparação para concursos

Responda sempre considerando o contexto completo do usuário.
`
  }

  private async generateSuggestions(context: SatiContext, message: string): Promise<string[]> {
    // Gerar sugestões baseadas no contexto
    return [
      'Que tal fazer uma pausa para hidratação?',
      'Posso te ajudar a criar um plano de estudos?',
      'Vamos revisar suas metas da semana?'
    ]
  }

  private async generateActions(context: SatiContext, message: string) {
    // Gerar ações específicas baseadas no contexto
    return [
      {
        type: 'create_study_plan',
        label: 'Criar Plano de Estudos',
        data: { subject: 'matemática' }
      },
      {
        type: 'start_pomodoro',
        label: 'Iniciar Pomodoro',
        data: { duration: 25 }
      }
    ]
  }
}
```

## 📋 FASE 4: Interface Chat

### 4.1 **Componente de Chat**

```typescript
// app/components/sati/SatiChat.tsx
'use client'

import { useState, useEffect, useRef } from 'react'
import { useSatiStore } from '../../stores/satiStore'
import { SatiMessage } from '../../lib/sati/types'

export default function SatiChat() {
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const {
    currentConversation,
    messages,
    sendMessage,
    createConversation,
    loadConversations
  } = useSatiStore()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    loadConversations()
  }, [])

  const handleSendMessage = async () => {
    if (!message.trim() || isLoading) return

    setIsLoading(true)
    try {
      await sendMessage(message)
      setMessage('')
    } catch (error) {
      console.error('Error sending message:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="border-b p-4">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          SATI - Sua Assistente Virtual
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Como posso te ajudar hoje?
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        {isLoading && <LoadingMessage />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <div className="flex space-x-2">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua mensagem..."
            className="flex-1 p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!message.trim() || isLoading}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Enviar
          </button>
        </div>
      </div>
    </div>
  )
}

function ChatMessage({ message }: { message: SatiMessage }) {
  const isUser = message.role === 'user'
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        <p className="text-xs mt-1 opacity-70">
          {new Date(message.created_at).toLocaleTimeString()}
        </p>
      </div>
    </div>
  )
}

function LoadingMessage() {
  return (
    <div className="flex justify-start">
      <div className="bg-gray-200 dark:bg-gray-700 px-4 py-2 rounded-lg">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>
    </div>
  )
}
```

### 4.2 **Store da SATI**

```typescript
// stores/satiStore.ts
import { create } from 'zustand'
import { SatiService } from '../lib/sati/satiService'
import { SatiConversation, SatiMessage, SatiResponse } from '../lib/sati/types'
import { supabase } from '../lib/supabase/client'

interface SatiState {
  conversations: SatiConversation[]
  currentConversation: SatiConversation | null
  messages: SatiMessage[]
  isLoading: boolean
  error: string | null
  
  // Actions
  loadConversations: () => Promise<void>
  createConversation: () => Promise<void>
  selectConversation: (id: string) => Promise<void>
  sendMessage: (message: string) => Promise<SatiResponse>
  clearError: () => void
}

const satiService = new SatiService(process.env.MARITACA_API_KEY!)

export const useSatiStore = create<SatiState>((set, get) => ({
  conversations: [],
  currentConversation: null,
  messages: [],
  isLoading: false,
  error: null,

  loadConversations: async () => {
    try {
      const { data, error } = await supabase
        .from('sati_conversations')
        .select('*')
        .order('updated_at', { ascending: false })

      if (error) throw error
      set({ conversations: data || [] })
    } catch (error) {
      set({ error: error.message })
    }
  },

  createConversation: async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('User not authenticated')

      const { data, error } = await supabase
        .from('sati_conversations')
        .insert({ user_id: user.id })
        .select()
        .single()

      if (error) throw error
      
      set((state) => ({
        conversations: [data, ...state.conversations],
        currentConversation: data,
        messages: []
      }))
    } catch (error) {
      set({ error: error.message })
    }
  },

  selectConversation: async (id: string) => {
    try {
      const conversation = get().conversations.find(c => c.id === id)
      if (!conversation) return

      const { data, error } = await supabase
        .from('sati_messages')
        .select('*')
        .eq('conversation_id', id)
        .order('created_at', { ascending: true })

      if (error) throw error

      set({
        currentConversation: conversation,
        messages: data || []
      })
    } catch (error) {
      set({ error: error.message })
    }
  },

  sendMessage: async (message: string) => {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('User not authenticated')

      let { currentConversation } = get()
      
      // Criar conversa se não existir
      if (!currentConversation) {
        await get().createConversation()
        currentConversation = get().currentConversation
      }

      set({ isLoading: true, error: null })

      const response = await satiService.processMessage({
        message,
        conversationId: currentConversation?.id
      }, user.id)

      // Recarregar mensagens
      await get().selectConversation(currentConversation!.id)

      set({ isLoading: false })
      return response
    } catch (error) {
      set({ error: error.message, isLoading: false })
      throw error
    }
  },

  clearError: () => set({ error: null })
}))
```

## 📋 FASE 5: Integração WhatsApp (Opcional)

### 5.1 **Webhook WhatsApp**

```typescript
// pages/api/sati/whatsapp.ts
import { NextApiRequest, NextApiResponse } from 'next'
import { SatiService } from '../../../lib/sati/satiService'

const satiService = new SatiService(process.env.MARITACA_API_KEY!)

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    // Verificação do webhook
    const mode = req.query['hub.mode']
    const token = req.query['hub.verify_token']
    const challenge = req.query['hub.challenge']

    if (mode === 'subscribe' && token === process.env.WHATSAPP_VERIFY_TOKEN) {
      res.status(200).send(challenge)
    } else {
      res.status(403).send('Forbidden')
    }
  } else if (req.method === 'POST') {
    // Processar mensagens
    try {
      const { entry } = req.body
      
      for (const item of entry) {
        const changes = item.changes || []
        
        for (const change of changes) {
          if (change.field === 'messages') {
            const messages = change.value.messages || []
            
            for (const message of messages) {
              await processWhatsAppMessage(message)
            }
          }
        }
      }
      
      res.status(200).json({ success: true })
    } catch (error) {
      console.error('WhatsApp webhook error:', error)
      res.status(500).json({ error: 'Internal server error' })
    }
  }
}

async function processWhatsAppMessage(message: any) {
  // Implementar processamento de mensagem WhatsApp
  // 1. Identificar usuário
  // 2. Processar mensagem com SATI
  // 3. Enviar resposta via WhatsApp API
}
```

## 🚨 Considerações Críticas para LLM

### ⚠️ Segurança:
- **NUNCA** expor API keys no frontend
- **SEMPRE** validar autenticação antes de processar
- **IMPLEMENTAR** rate limiting para evitar abuso
- **USAR** RLS para proteger dados

### ✅ Performance:
- **CACHE** embeddings para evitar regeneração
- **LIMITAR** tamanho do contexto RAG
- **IMPLEMENTAR** timeout para requests
- **MONITORAR** uso de tokens da API

### 🔧 Troubleshooting:
- **LOGS** detalhados para debug
- **FALLBACK** para quando Maritaca falhar
- **VALIDAÇÃO** de responses da API
- **BACKUP** de conversas importantes

---

**Anterior:** [04 - Migração Supabase](./04-migracao-supabase.md) | **Próximo:** [06 - Validação e Testes](./06-validacao-testes.md)
