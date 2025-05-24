# Prompts Específicos - StayFocus Migration & SATI

## 🎯 Prompts Prontos para Uso Imediato

Esta seção contém prompts específicos já personalizados para o projeto StayFocus que você pode usar diretamente com LLMs.

---

## 🏗️ MIGRAÇÃO - PROMPTS ESPECÍFICOS

### 1. Migração PomodoroStore

```markdown
Você é um desenvolvedor experiente trabalhando na migração do StayFocus para Supabase. Analise o arquivo `app/stores/pomodoroStore.ts` e migre-o seguindo TDD:

**FASE 1 - ANÁLISE E TESTES**:
1. Estude a estrutura atual do pomodoroStore
2. Identifique todas as funcionalidades (timer, sessões, estatísticas)
3. Crie testes que cobrem:
   - Iniciar/pausar/parar timer
   - Salvar sessões completadas
   - Calcular estatísticas
   - Sincronização com Supabase
   - Fallback para localStorage

**FASE 2 - IMPLEMENTAÇÃO**:
1. Crie schema SQL para tabela `pomodoro_sessions`
2. Implemente `PomodoroService` com métodos CRUD
3. Atualize store para usar o service
4. Mantenha interface existente intacta

**FASE 3 - VALIDAÇÃO**:
1. Execute migração de dados existentes
2. Teste funcionamento online/offline
3. Valide performance e sincronização

**ARQUIVOS NECESSÁRIOS**:
- `supabase/migrations/create_pomodoro_sessions.sql`
- `lib/services/PomodoroService.ts`
- `app/stores/pomodoroStore.ts` (atualizado)
- `__tests__/stores/pomodoroStore.test.ts`

Execute em ordem: Análise → Testes → Implementação → Validação.
```

### 2. Migração AtividadesStore

```markdown
Migre o `app/stores/atividadesStore.ts` para Supabase mantendo todas as funcionalidades de gestão de tarefas:

**CONTEXTO ATUAL**:
- Store gerencia tarefas/atividades do usuário
- Funcionalidades: CRUD, priorização, categorização, status
- Integração com sistema Pomodoro

**TAREFA TDD**:
1. **TESTES PRIMEIRO**:
   ```typescript
   describe('AtividadesStore Migration', () => {
     test('should migrate existing tasks to Supabase')
     test('should maintain CRUD operations')
     test('should handle priority and categories')
     test('should sync with Pomodoro sessions')
     test('should work offline with sync')
   })
   ```

2. **IMPLEMENTAÇÃO**:
   - Schema SQL com RLS para tarefas
   - AtividadesService com operações assíncronas
   - Store atualizado com sync automático
   - Migração de dados localStorage

3. **FEATURES ESPECÍFICAS**:
   - Soft delete para histórico
   - Indexação para performance
   - Relação com sessões Pomodoro
   - Categorização e tags

**CRITÉRIOS DE SUCESSO**:
- [ ] Todas as tarefas migradas
- [ ] CRUD funcionando perfeitamente
- [ ] Sincronização online/offline
- [ ] Performance mantida
- [ ] Testes passando (>90% coverage)

Foque em manter a UX existente enquanto adiciona robustez do backend.
```

### 3. Setup Inicial Completo

```markdown
Configure o projeto StayFocus para usar Supabase como backend principal:

**SETUP COMPLETO NECESSÁRIO**:

1. **DEPENDÊNCIAS**:
   ```bash
   npm install @supabase/supabase-js @supabase/auth-helpers-nextjs
   npm install -D @types/node
   ```

2. **CONFIGURAÇÃO**:
   - Criar projeto no Supabase
   - Configurar autenticação (email/password + Google)
   - Setup RLS (Row Level Security)
   - Configurar variáveis ambiente

3. **ESTRUTURA BASE**:
   ```
   lib/
   ├── supabase.ts (cliente)
   ├── auth.ts (autenticação)
   └── services/ (serviços por domínio)
   
   supabase/
   ├── config.toml
   └── migrations/
   ```

4. **VALIDAÇÃO**:
   - Conexão estabelecida
   - Autenticação funcionando
   - RLS configurado
   - Migrations rodando

**ARQUIVOS PARA CRIAR**:
- `.env.local` com variáveis Supabase
- `lib/supabase.ts` - cliente configurado
- `lib/auth.ts` - helpers de autenticação
- `middleware.ts` - proteção de rotas
- `supabase/config.toml` - configuração local

Execute configuração → teste → validação → documentação.
```

---

## 🤖 SATI - PROMPTS ESPECÍFICOS

### 1. Core SATI Implementation

```markdown
Implemente o serviço principal do SATI (Sistema de Assistência Técnica Inteligente) para o StayFocus:

**ARQUITETURA OBJETIVO**:
- Core service que analisa contexto do usuário
- Integração com Maritaca AI para geração de respostas
- Sistema de memória para manter contexto de conversas
- Análise preditiva de produtividade

**IMPLEMENTAÇÃO TDD**:

1. **TESTES CORE**:
   ```typescript
   describe('SATIService', () => {
     test('should analyze user productivity patterns')
     test('should generate contextual suggestions')
     test('should maintain conversation memory')
     test('should integrate with Maritaca AI')
     test('should handle rate limiting')
   })
   ```

2. **IMPLEMENTAR SERVIÇOS**:
   ```typescript
   // lib/services/sati/SATIService.ts
   class SATIService {
     async analyzeUserContext(): Promise<UserContext>
     async generateSuggestion(context: UserContext): Promise<Suggestion>
     async processMessage(message: string): Promise<Response>
   }
   ```

3. **INTEGRAÇÃO MARITACA**:
   - Cliente HTTP para API Maritaca
   - Rate limiting e retry logic
   - Context window management
   - Response streaming

**FUNCIONALIDADES ESPECÍFICAS**:
- Análise de padrões de produtividade
- Sugestões proativas baseadas em contexto
- Integração com dados de Pomodoro e tarefas
- Memória de conversas para continuidade

**VALIDAÇÃO**:
- [ ] Integração Maritaca funcionando
- [ ] Context analysis preciso
- [ ] Suggestions relevantes
- [ ] Performance <2s
- [ ] Error handling robusto

Foque em criar um assistente verdadeiramente útil que entende o contexto do usuário.
```

### 2. Sistema RAG para SATI

```markdown
Implemente sistema RAG (Retrieval-Augmented Generation) para enriquecer as respostas do SATI:

**OBJETIVO**:
Criar conhecimento contextual baseado nos dados do usuário para gerar respostas mais precisas e personalizadas.

**COMPONENTES DO SISTEMA**:

1. **EMBEDDING SERVICE**:
   ```typescript
   class EmbeddingService {
     async generateEmbedding(text: string): Promise<number[]>
     async batchEmbed(texts: string[]): Promise<number[][]>
     async updateUserKnowledgeBase(userId: string): Promise<void>
   }
   ```

2. **VECTOR STORE**:
   - Usar pgvector no Supabase
   - Indexação otimizada para busca
   - Hybrid search (vector + text)

3. **KNOWLEDGE BASE**:
   - Embeddings de tarefas do usuário
   - Padrões de produtividade históricos
   - Preferências e contextos anteriores

**IMPLEMENTAÇÃO TDD**:
1. Testes de geração de embeddings
2. Testes de busca semântica
3. Testes de ranking de relevância
4. Testes de atualização da knowledge base

**SCHEMA SUPABASE**:
```sql
CREATE TABLE user_embeddings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  content TEXT NOT NULL,
  embedding VECTOR(1536),
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX ON user_embeddings USING ivfflat (embedding vector_cosine_ops);
```

**VALIDAÇÃO**:
- [ ] Embeddings gerados corretamente
- [ ] Busca semântica funcional
- [ ] Ranking de relevância preciso
- [ ] Performance <500ms para queries
- [ ] Knowledge base atualizada automaticamente

Execute: Schema → Embeddings → Search → Integration → Validation.
```

### 3. Interface Chat do SATI

```markdown
Crie a interface de chat do SATI integrada ao StayFocus:

**DESIGN REQUIREMENTS**:
- Chat flutuante/modal que não atrapalha workflow
- Design consistente com StayFocus (Tailwind)
- Suporte a markdown nas respostas
- Indicadores de typing e loading
- Histórico de conversas

**COMPONENTES REACT**:

1. **SATIChat Container**:
   ```typescript
   interface SATIChatProps {
     isOpen: boolean
     onClose: () => void
     userId: string
   }
   ```

2. **MessageBubble**:
   - User messages (right aligned)
   - SATI responses (left aligned, markdown support)
   - Timestamp e status de entrega

3. **ChatInput**:
   - Textarea com auto-resize
   - Send button e shortcuts (Enter)
   - Voice input (futuro)

**FUNCIONALIDADES**:
- Suggestions proativas baseadas em contexto
- Quick actions (criar tarefa, iniciar Pomodoro)
- Histórico persistente de conversas
- Notificações de sugestões

**ESTADO E HOOKS**:
```typescript
const useSATIChat = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  
  const sendMessage = async (content: string) => { /* ... */ }
  const loadHistory = async () => { /* ... */ }
  
  return { messages, sendMessage, isTyping, suggestions }
}
```

**VALIDAÇÃO**:
- [ ] Interface responsiva
- [ ] Markdown rendering correto
- [ ] Histórico persistente
- [ ] Performance smooth
- [ ] Acessibilidade (WCAG 2.1)
- [ ] Integração com SATI service

Foque em UX excelente que torna o SATI uma ferramenta indispensável.
```

---

## 🔧 DEBUGGING E TROUBLESHOOTING

### 1. Debug de Performance

```markdown
Analise e otimize performance da aplicação StayFocus após migração:

**PROBLEMAS COMUNS A INVESTIGAR**:
1. Queries lentas no Supabase
2. Re-renders desnecessários nos stores
3. Bundle size aumentado
4. Latência da API Maritaca

**FERRAMENTAS DE ANÁLISE**:
```bash
# Bundle analysis
npx @next/bundle-analyzer
npm run build

# Performance profiling
lighthouse --view
npm run dev -- --analyze
```

**CHECKLIST DE OTIMIZAÇÃO**:
- [ ] Database queries otimizadas (indexes, explain analyze)
- [ ] React components memoizados adequadamente
- [ ] Code splitting implementado
- [ ] Images otimizadas
- [ ] API calls com cache adequado

**MÉTRICAS ALVO**:
- First Contentful Paint: <1.5s
- Time to Interactive: <3s
- Database queries: <100ms
- SATI response: <2s

Identifique gargalos → implemente otimizações → meça resultados → itere.
```

### 2. Debug de Sincronização

```markdown
Diagnostique e corrija problemas de sincronização entre localStorage e Supabase:

**SINTOMAS COMUNS**:
- Dados desatualizados
- Conflitos de sincronização
- Perda de dados offline
- Estado inconsistente

**ESTRATÉGIA DE DEBUG**:

1. **LOGGING DETALHADO**:
   ```typescript
   const debugSync = {
     local: () => console.log('LocalStorage state:', localStorage.getItem('key')),
     remote: () => console.log('Supabase state:', await supabase.from('table').select()),
     conflict: (local, remote) => console.log('Conflict detected:', { local, remote })
   }
   ```

2. **VALIDAÇÃO DE ESTADO**:
   - Comparar timestamps
   - Verificar integridade de dados
   - Detectar conflitos automáticos

3. **ESTRATÉGIAS DE RESOLUÇÃO**:
   - Last-write-wins
   - Merge automático quando possível
   - User prompt para conflitos críticos

**IMPLEMENTAR RETRY LOGIC**:
```typescript
const syncWithRetry = async (operation: () => Promise<void>, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      await operation()
      return
    } catch (error) {
      if (i === maxRetries - 1) throw error
      await delay(1000 * Math.pow(2, i)) // exponential backoff
    }
  }
}
```

**VALIDAÇÃO**:
- [ ] Conflitos detectados e resolvidos
- [ ] Dados consistentes online/offline
- [ ] Recovery automático de falhas
- [ ] User feedback adequado

Foque em robustez e confiabilidade da sincronização.
```

---

## 🚀 DEPLOYMENT E PRODUÇÃO

### 1. Deploy Production-Ready

```markdown
Prepare e execute deploy seguro do StayFocus para produção:

**PRE-DEPLOYMENT CHECKLIST**:

1. **TESTES COMPLETOS**:
   ```bash
   npm run test              # Unit tests
   npm run test:e2e         # E2E tests
   npm run test:performance # Performance tests
   npm run lint             # Code quality
   npm run security-audit   # Security scan
   ```

2. **BUILD OPTIMIZATION**:
   ```bash
   npm run build
   npm run analyze          # Bundle analysis
   ```

3. **ENVIRONMENT SETUP**:
   - Supabase production project
   - Maritaca AI production keys
   - Monitoring tools configurados
   - Backup procedures testados

**DEPLOYMENT STRATEGY**:
- Blue-Green deployment
- Feature flags para SATI
- Database migration strategy
- Rollback procedures

**MONITORING SETUP**:
```typescript
// Error tracking
import { trackError } from '@/lib/monitoring'

// Performance monitoring
import { measurePerformance } from '@/lib/analytics'

// Usage analytics
import { trackUserAction } from '@/lib/tracking'
```

**POST-DEPLOY VALIDATION**:
- [ ] Health checks passing
- [ ] Database migrations successful
- [ ] SATI funcionando corretamente
- [ ] Performance within SLA
- [ ] No errors critical
- [ ] Monitoring ativo

Execute: Validate → Deploy → Monitor → Optimize.
```

---

## 📚 QUICK REFERENCE

### Comando Rápidos para LLM

```markdown
# ANÁLISE RÁPIDA
"Analise o arquivo [NOME_ARQUIVO] e identifique [FUNCIONALIDADES/PROBLEMAS]"

# IMPLEMENTAÇÃO TDD
"Implemente [FUNCIONALIDADE] seguindo TDD: testes primeiro, depois implementação"

# DEBUG ESPECÍFICO
"Debug o problema [DESCRIÇÃO] no componente [NOME_COMPONENTE]"

# OTIMIZAÇÃO
"Otimize performance de [ÁREA_ESPECÍFICA] com foco em [MÉTRICA]"

# MIGRAÇÃO
"Migre [STORE_NAME] de localStorage para Supabase mantendo funcionalidades"
```

### Estrutura Padrão de Resposta

```markdown
**ANÁLISE**: [O que foi identificado]
**SOLUÇÃO**: [Abordagem proposta]
**IMPLEMENTAÇÃO**: [Código/passos específicos]
**TESTES**: [Como validar]
**CRITÉRIOS**: [Lista de verificação]
```

---

Estes prompts específicos cobrem todos os cenários comuns da migração e implementação do SATI, garantindo comunicação eficiente e resultados consistentes com LLMs! 🚀
