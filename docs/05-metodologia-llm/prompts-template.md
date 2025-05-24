# Templates de Prompts para LLM - StayFocus

## 📋 Visão Geral

Esta documentação contém templates de prompts otimizados para uso com LLMs durante a migração do StayFocus para Supabase e implementação do SATI. Os prompts seguem a metodologia TDD (Test-Driven Development) e abordagem "one-shot" para máxima eficiência.

## 🎯 Princípios dos Templates

1. **TDD First** - Sempre criar testes antes da implementação
2. **One-Shot** - Prompt completo com todo contexto necessário
3. **Específico** - Instruções claras e objetivos bem definidos
4. **Validável** - Critérios de sucesso mensuráveis
5. **Contextual** - Informações relevantes do projeto incluídas

---

## 🏗️ FASE 1: CONFIGURAÇÃO E MIGRAÇÃO

### 1.1 Setup Inicial do Supabase

```markdown
# PROMPT: Setup Inicial Supabase - StayFocus

## CONTEXTO
Você é um desenvolvedor experiente trabalhando no projeto StayFocus, uma aplicação Next.js de produtividade que usa localStorage. Precisa configurar Supabase como backend.

## ESTRUTURA ATUAL
- Next.js 14 com TypeScript
- Zustand para gerenciamento de estado
- Stores locais: pomodoroStore, atividadesStore, perfilStore, etc.
- TailwindCSS para styling

## TAREFA
Configure o Supabase no projeto seguindo TDD:

1. **CRIAR TESTES PRIMEIRO**:
   - Teste de conexão com Supabase
   - Teste de autenticação básica
   - Teste de configuração de ambiente

2. **IMPLEMENTAR**:
   - Instalar dependências do Supabase
   - Configurar variáveis de ambiente
   - Criar cliente Supabase
   - Setup de autenticação

3. **VALIDAR**:
   - Conexão estabelecida
   - Autenticação funcionando
   - Testes passando

## ARQUIVOS PARA MODIFICAR/CRIAR
- `.env.local`
- `lib/supabase.ts`
- `__tests__/supabase.test.ts`
- `package.json`

## CRITÉRIOS DE SUCESSO
- [ ] Supabase conectado
- [ ] Testes passando
- [ ] Autenticação configurada
- [ ] Variáveis de ambiente seguras

Execute em ordem: testes → implementação → validação.
```

### 1.2 Migração de Store Específico

```markdown
# PROMPT: Migração Store - StayFocus TDD

## CONTEXTO
Migrar [NOME_DO_STORE] do localStorage para Supabase mantendo funcionalidade existente.

## STORE ATUAL
Analise o arquivo: `app/stores/[NOME_DO_STORE].ts`

## TAREFA TDD
1. **RED** - Criar testes que falham:
   - Teste de CRUD operations
   - Teste de sincronização
   - Teste de migração de dados
   - Teste de fallback para localStorage

2. **GREEN** - Implementar mínimo necessário:
   - Schema SQL do Supabase
   - Service layer para API
   - Atualizar store Zustand
   - Migração de dados existentes

3. **REFACTOR** - Otimizar:
   - Performance
   - Error handling
   - Type safety
   - Cache strategies

## REQUISITOS TÉCNICOS
- Manter interface do store existente
- RLS (Row Level Security) configurado
- Migração automática de dados localStorage
- Fallback para localStorage em caso de erro
- Sincronização bidirecional

## ARQUIVOS ENVOLVIDOS
- `supabase/migrations/[timestamp]_[store_name].sql`
- `lib/services/[store_name]Service.ts`
- `app/stores/[NOME_DO_STORE].ts`
- `__tests__/stores/[NOME_DO_STORE].test.ts`

## VALIDAÇÃO
- [ ] Todos os testes passando
- [ ] Dados migrados corretamente
- [ ] Performance mantida
- [ ] RLS funcionando
- [ ] Rollback possível

Execute: RED → GREEN → REFACTOR → Validate
```

---

## 🤖 FASE 2: IMPLEMENTAÇÃO SATI

### 2.1 Core SATI Service

```markdown
# PROMPT: SATI Core Service - TDD Implementation

## CONTEXTO
Implementar o serviço principal do SATI (Sistema de Assistência Técnica Inteligente) usando Maritaca AI.

## ARQUITETURA ALVO
- Core Service com padrão Repository
- Integração com Maritaca AI
- Sistema RAG com embeddings
- Análise de contexto avançada

## TAREFA TDD
1. **ESCREVER TESTES PRIMEIRO**:
   ```typescript
   describe('SATIService', () => {
     test('should analyze user context')
     test('should generate contextual suggestions')
     test('should handle conversation flow')
     test('should integrate with Maritaca AI')
     test('should manage embeddings')
   })
   ```

2. **IMPLEMENTAR MÍNIMO**:
   - Interface ISATIService
   - SATIService class
   - Maritaca client integration
   - Context analysis logic

3. **REFATORAR**:
   - Error handling robusto
   - Caching inteligente
   - Performance optimization

## ESPECIFICAÇÕES TÉCNICAS
- TypeScript com strict mode
- Dependency injection pattern
- Async/await com proper error handling
- Rate limiting para API calls
- Logging estruturado

## ARQUIVOS PARA CRIAR
- `lib/services/sati/SATIService.ts`
- `lib/services/sati/MaritacaClient.ts`
- `lib/services/sati/interfaces.ts`
- `__tests__/services/sati/SATIService.test.ts`

## CRITÉRIOS DE SUCESSO
- [ ] Testes unitários passando (>90% coverage)
- [ ] Integração Maritaca funcionando
- [ ] Context analysis preciso
- [ ] Performance <2s response time
- [ ] Error handling robusto

Execute metodologia: Test → Code → Refactor → Validate
```

### 2.2 Sistema RAG

```markdown
# PROMPT: RAG System Implementation - StayFocus SATI

## CONTEXTO
Implementar sistema RAG (Retrieval-Augmented Generation) para o SATI com busca vetorial e knowledge base.

## OBJETIVOS
- Busca semântica em dados do usuário
- Contexto enriquecido para IA
- Knowledge base dinâmica
- Embeddings otimizados

## ABORDAGEM TDD
1. **TESTES PRIMEIRO**:
   ```typescript
   describe('RAGSystem', () => {
     test('should generate embeddings for user data')
     test('should perform semantic search')
     test('should rank results by relevance')
     test('should update knowledge base')
     test('should handle large datasets')
   })
   ```

2. **IMPLEMENTAÇÃO MÍNIMA**:
   - Embedding service
   - Vector search engine
   - Knowledge base manager
   - Ranking algorithm

3. **OTIMIZAÇÃO**:
   - Batch processing
   - Caching strategy
   - Index optimization

## STACK TÉCNICO
- Supabase Vector (pgvector)
- Maritaca embeddings
- PostgreSQL full-text search
- Hybrid search (vector + text)

## DELIVERABLES
- `lib/services/rag/RAGService.ts`
- `lib/services/rag/EmbeddingService.ts`
- `lib/services/rag/VectorStore.ts`
- `supabase/migrations/create_embeddings_tables.sql`
- `__tests__/services/rag/RAGService.test.ts`

## VALIDAÇÃO
- [ ] Embeddings gerados corretamente
- [ ] Busca semântica precisa
- [ ] Performance <1s para queries
- [ ] Knowledge base atualizada
- [ ] Testes com coverage >85%

Metodologia: Write Tests → Implement → Optimize → Test
```

### 2.3 Interface de Chat

```markdown
# PROMPT: SATI Chat Interface - React TDD

## CONTEXTO
Criar interface de chat para o SATI com React/Next.js seguindo TDD e design system existente.

## DESIGN REQUIREMENTS
- Integração com TailwindCSS existente
- Responsive design
- Acessibilidade (WCAG 2.1)
- Animações suaves
- Estado de loading/typing

## TDD APPROACH
1. **COMPONENT TESTS FIRST**:
   ```typescript
   describe('SATIChat', () => {
     test('renders chat interface')
     test('handles message sending')
     test('displays conversation history')
     test('shows typing indicators')
     test('handles error states')
   })
   ```

2. **IMPLEMENT COMPONENTS**:
   - ChatContainer
   - MessageBubble
   - InputArea
   - TypingIndicator
   - SuggestionCards

3. **INTEGRATION TESTS**:
   - WebSocket connections
   - Real-time updates
   - State management

## TECHNICAL SPECS
- React 18 with hooks
- TypeScript strict mode
- Zustand for state
- React Testing Library
- Accessibility first

## COMPONENT STRUCTURE
```
app/components/sati/
├── SATIChat.tsx
├── MessageBubble.tsx
├── ChatInput.tsx
├── TypingIndicator.tsx
├── SuggestionCard.tsx
└── hooks/
    ├── useSATIChat.ts
    └── useChat.ts
```

## VALIDATION CRITERIA
- [ ] All components tested
- [ ] Responsive on all devices
- [ ] Accessibility score >95%
- [ ] Performance budget met
- [ ] Integration with SATI service

Execute: Test Components → Build UI → Test Integration → Polish
```

---

## 🔧 FASE 3: OTIMIZAÇÃO E TESTES

### 3.1 Performance Testing

```markdown
# PROMPT: Performance Testing & Optimization - StayFocus

## CONTEXTO
Implementar testes de performance e otimizações para a aplicação migrada.

## OBJETIVOS DE PERFORMANCE
- Lighthouse Score >90
- First Contentful Paint <1.5s
- Time to Interactive <3s
- Database queries <100ms
- SATI response time <2s

## TDD PERFORMANCE
1. **PERFORMANCE TESTS**:
   ```typescript
   describe('Performance Tests', () => {
     test('page load time under 3s')
     test('database queries under 100ms')
     test('SATI response under 2s')
     test('bundle size under 500kb')
   })
   ```

2. **IMPLEMENT OPTIMIZATIONS**:
   - Code splitting
   - Image optimization
   - Database indexing
   - Caching strategies
   - Bundle analysis

3. **MONITOR & IMPROVE**:
   - Performance metrics
   - Real user monitoring
   - Automated testing

## TOOLS & TECHNIQUES
- Next.js performance features
- React.memo and useMemo
- Database indexing
- CDN optimization
- Service worker caching

## DELIVERABLES
- Performance test suite
- Optimization implementations
- Monitoring dashboard
- Performance budget configuration

## SUCCESS METRICS
- [ ] All performance tests passing
- [ ] Lighthouse score >90
- [ ] Bundle size optimized
- [ ] Database queries optimized
- [ ] Real user metrics improved

Focus: Measure → Optimize → Test → Monitor
```

### 3.2 End-to-End Testing

```markdown
# PROMPT: E2E Testing Suite - StayFocus Migration

## CONTEXTO
Criar suite completa de testes end-to-end para validar migração e funcionalidades SATI.

## CENÁRIOS CRÍTICOS
1. **User Journey Completo**:
   - Registro/Login
   - Criação de tarefas
   - Sessões Pomodoro
   - Interação com SATI
   - Exportação de dados

2. **Migration Scenarios**:
   - Migração de dados existentes
   - Sincronização online/offline
   - Rollback procedures
   - Data integrity

## TDD E2E APPROACH
1. **WRITE E2E TESTS FIRST**:
   ```typescript
   describe('Complete User Journey', () => {
     test('user can migrate and use app')
     test('SATI provides contextual help')
     test('data persists across sessions')
     test('offline mode works correctly')
   })
   ```

2. **IMPLEMENT TEST INFRASTRUCTURE**:
   - Playwright setup
   - Test data factories
   - Page object models
   - CI/CD integration

3. **VALIDATE EVERYTHING**:
   - All user flows working
   - Performance within limits
   - No regressions

## TECH STACK
- Playwright for E2E
- Docker for test environment
- GitHub Actions for CI
- Test data seeding

## TEST STRUCTURE
```
e2e/
├── tests/
│   ├── migration.spec.ts
│   ├── sati.spec.ts
│   ├── user-journey.spec.ts
│   └── performance.spec.ts
├── fixtures/
├── page-objects/
└── utils/
```

## ACCEPTANCE CRITERIA
- [ ] All critical paths tested
- [ ] Migration scenarios covered
- [ ] SATI interactions validated
- [ ] Performance regression tests
- [ ] CI/CD pipeline green

Approach: Plan Tests → Build Infrastructure → Execute → Report
```

---

## 🚀 FASE 4: DEPLOYMENT E MONITORAMENTO

### 4.1 Production Deployment

```markdown
# PROMPT: Production Deployment - StayFocus

## CONTEXTO
Realizar deploy seguro para produção da aplicação migrada com SATI.

## ESTRATÉGIA DE DEPLOY
- Blue-Green deployment
- Feature flags para SATI
- Database migration strategy
- Rollback procedures
- Monitoring setup

## PRE-DEPLOYMENT CHECKLIST
1. **TESTS VALIDATION**:
   - All unit tests passing
   - E2E tests successful
   - Performance tests within limits
   - Security scan clean

2. **INFRASTRUCTURE READY**:
   - Supabase production setup
   - Environment variables configured
   - Monitoring tools installed
   - Backup procedures tested

## DEPLOYMENT TASKS
1. **DATABASE MIGRATION**:
   ```sql
   -- Execute migration scripts
   -- Validate data integrity
   -- Setup RLS policies
   -- Create indexes
   ```

2. **APPLICATION DEPLOY**:
   - Build optimization
   - Environment configuration
   - Health checks
   - Feature flag setup

3. **POST-DEPLOY VALIDATION**:
   - Smoke tests
   - Performance monitoring
   - Error tracking
   - User acceptance testing

## MONITORING SETUP
- Application performance monitoring
- Database performance tracking
- SATI usage analytics
- Error tracking and alerting

## SUCCESS CRITERIA
- [ ] Zero-downtime deployment
- [ ] All health checks passing
- [ ] Performance within SLA
- [ ] No critical errors
- [ ] SATI functioning correctly
- [ ] Monitoring active

Execute: Validate → Deploy → Monitor → Optimize
```

---

## 📚 TEMPLATES DE USO GERAL

### Template Base para Qualquer Tarefa

```markdown
# PROMPT: [TÍTULO DA TAREFA] - StayFocus TDD

## CONTEXTO
[Descrição do contexto atual do projeto]

## OBJETIVO
[O que precisa ser alcançado]

## ABORDAGEM TDD
1. **RED - Escrever Testes que Falham**:
   [Especificar testes necessários]

2. **GREEN - Implementar Mínimo Necessário**:
   [Implementação básica para passar nos testes]

3. **REFACTOR - Melhorar Código**:
   [Otimizações e melhorias]

## ESPECIFICAÇÕES TÉCNICAS
[Requisitos técnicos específicos]

## ARQUIVOS ENVOLVIDOS
[Lista de arquivos a criar/modificar]

## CRITÉRIOS DE SUCESSO
- [ ] [Critério 1]
- [ ] [Critério 2]
- [ ] [Critério 3]

## VALIDAÇÃO
[Como validar se a tarefa foi concluída com sucesso]

Execute: [Sequência específica de passos]
```

### Template para Debug/Troubleshooting

```markdown
# PROMPT: Debug/Fix - [PROBLEMA] - StayFocus

## PROBLEMA IDENTIFICADO
[Descrição clara do problema]

## CONTEXTO DO ERRO
[Onde ocorre, quando ocorre, logs relevantes]

## INVESTIGAÇÃO SISTEMÁTICA
1. **REPRODUZIR PROBLEMA**:
   - Criar teste que reproduz o bug
   - Documentar steps para reprodução
   - Identificar condições específicas

2. **DIAGNOSTICAR CAUSA RAIZ**:
   - Analisar logs e stack traces
   - Verificar dados relacionados
   - Identificar componentes afetados

3. **IMPLEMENTAR FIX**:
   - Corrigir causa raiz
   - Adicionar validações preventivas
   - Atualizar testes existentes

## VALIDAÇÃO DO FIX
- [ ] Bug reproduzido e corrigido
- [ ] Testes passando
- [ ] Não introduziu regressões
- [ ] Documentação atualizada

Execute: Reproduce → Diagnose → Fix → Validate
```

---

## 🎯 COMO USAR OS TEMPLATES

### 1. Escolha o Template Apropriado
- **Setup/Config**: Use templates de configuração
- **Migração**: Use templates específicos de migração
- **SATI**: Use templates de implementação AI
- **Debug**: Use template de troubleshooting

### 2. Personalize o Contexto
- Substitua placeholders `[NOME_DO_STORE]`
- Adicione contexto específico do projeto
- Inclua informações relevantes da codebase

### 3. Execute Metodologia TDD
- Sempre comece com testes
- Implemente o mínimo necessário
- Refatore para qualidade
- Valide completamente

### 4. Valide Critérios de Sucesso
- Verifique todos os checkboxes
- Execute testes automatizados
- Confirme performance
- Documente resultados

---

## 📝 NOTAS IMPORTANTES

1. **Sempre incluir contexto completo** no prompt
2. **Especificar arquivos relevantes** para análise
3. **Definir critérios de sucesso mensuráveis**
4. **Seguir metodologia TDD rigorosamente**
5. **Validar cada etapa antes de prosseguir**

Estes templates garantem comunicação eficiente com LLMs e resultados consistentes seguindo as melhores práticas de desenvolvimento.
