# 06 - Validação e Testes

## 🎯 Estratégia de Validação

### Objetivos:
1. **Garantir funcionalidade** de cada componente migrado
2. **Validar integração** entre componentes
3. **Verificar performance** e usabilidade
4. **Assegurar segurança** dos dados
5. **Confirmar compatibilidade** com diferentes cenários

### Princípios:
- **Validação incremental** após cada mudança
- **Testes automatizados** sempre que possível
- **Validação manual** para UX/UI
- **Performance benchmarking** contínuo

## 📋 FASE 1: Validação da Migração Supabase

### 1.1 **Testes de Conectividade**

#### A. Teste de Conexão Básica
```typescript
// test/supabase/connection.test.ts
import { supabase } from '../../lib/supabase/client'

describe('Supabase Connection', () => {
  it('should connect to Supabase successfully', async () => {
    const { data, error } = await supabase
      .from('user_preferences')
      .select('count', { count: 'exact' })

    expect(error).toBeNull()
    expect(data).toBeDefined()
  })

  it('should authenticate users', async () => {
    // Teste com credenciais de teste
    const { data, error } = await supabase.auth.signInWithPassword({
      email: 'test@example.com',
      password: 'testpassword'
    })

    // Verificar se funciona ou se dá erro esperado
    expect(error?.message).toContain('Invalid login credentials')
  })
})
```

#### B. Comandos de Validação para LLM
```bash
# Executar sempre após mudanças de configuração
npm run test:supabase     # Testes específicos do Supabase
npm run test:auth         # Testes de autenticação
npm run test:rls          # Testes de Row Level Security
```

### 1.2 **Validação de Cada Store Migrada**

#### A. Template de Teste por Store
```typescript
// test/stores/alimentacaoStore.test.ts
import { renderHook, act } from '@testing-library/react'
import { useAlimentacaoStore } from '../../stores/alimentacaoStore'

describe('AlimentacaoStore Migration', () => {
  beforeEach(async () => {
    // Setup: limpar dados de teste
    await cleanupTestData()
  })

  it('should load user meals from Supabase', async () => {
    const { result } = renderHook(() => useAlimentacaoStore())
    
    await act(async () => {
      await result.current.loadRefeicoes('test-user-id')
    })

    expect(result.current.isLoading).toBe(false)
    expect(result.current.refeicoes).toBeDefined()
    expect(Array.isArray(result.current.refeicoes)).toBe(true)
  })

  it('should create new meal', async () => {
    const { result } = renderHook(() => useAlimentacaoStore())
    
    const newMeal = {
      tipo: 'almoço',
      descricao: 'Arroz, feijão, carne',
      data: new Date().toISOString()
    }

    await act(async () => {
      await result.current.adicionarRefeicao(newMeal)
    })

    expect(result.current.refeicoes).toHaveLength(1)
    expect(result.current.refeicoes[0].descricao).toBe(newMeal.descricao)
  })

  it('should update existing meal', async () => {
    // Criar refeição primeiro
    const { result } = renderHook(() => useAlimentacaoStore())
    
    await act(async () => {
      await result.current.adicionarRefeicao({
        tipo: 'café',
        descricao: 'Café com pão',
        data: new Date().toISOString()
      })
    })

    const mealId = result.current.refeicoes[0].id

    await act(async () => {
      await result.current.atualizarRefeicao(mealId, {
        descricao: 'Café com torrada'
      })
    })

    expect(result.current.refeicoes[0].descricao).toBe('Café com torrada')
  })

  it('should delete meal', async () => {
    // Criar e deletar refeição
    const { result } = renderHook(() => useAlimentacaoStore())
    
    await act(async () => {
      await result.current.adicionarRefeicao({
        tipo: 'lanche',
        descricao: 'Fruta',
        data: new Date().toISOString()
      })
    })

    const mealId = result.current.refeicoes[0].id

    await act(async () => {
      await result.current.removerRefeicao(mealId)
    })

    expect(result.current.refeicoes).toHaveLength(0)
  })

  it('should maintain backward compatibility', async () => {
    // Verificar se a API da store não mudou
    const { result } = renderHook(() => useAlimentacaoStore())
    
    // Verificar se métodos existem
    expect(typeof result.current.adicionarRefeicao).toBe('function')
    expect(typeof result.current.loadRefeicoes).toBe('function')
    expect(typeof result.current.atualizarRefeicao).toBe('function')
    expect(typeof result.current.removerRefeicao).toBe('function')
    
    // Verificar estrutura do estado
    expect(result.current.refeicoes).toBeDefined()
    expect(result.current.isLoading).toBeDefined()
    expect(result.current.error).toBeDefined()
  })

  afterEach(async () => {
    // Cleanup: limpar dados de teste
    await cleanupTestData()
  })
})

async function cleanupTestData() {
  // Implementar limpeza específica para teste
}
```

#### B. Checklist de Validação por Store
```typescript
// Para cada store migrada, validar:
interface StoreValidationChecklist {
  connectivity: boolean       // ✅ Conecta com Supabase
  crud_operations: boolean    // ✅ CRUD funcionando
  data_integrity: boolean     // ✅ Dados íntegros
  performance: boolean        // ✅ Performance aceitável
  error_handling: boolean     // ✅ Errors tratados
  backward_compatibility: boolean // ✅ API compatível
  realtime_sync: boolean      // ✅ Sync real-time
  offline_handling: boolean   // ✅ Funciona offline
}
```

### 1.3 **Validação de Componentes**

#### A. Teste de Componentes que Usam Stores
```typescript
// test/components/RegistroRefeicoes.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { RegistroRefeicoes } from '../../app/components/alimentacao/RegistroRefeicoes'

// Mock da store
jest.mock('../../stores/alimentacaoStore', () => ({
  useAlimentacaoStore: () => ({
    refeicoes: [],
    isLoading: false,
    error: null,
    adicionarRefeicao: jest.fn(),
    loadRefeicoes: jest.fn()
  })
}))

describe('RegistroRefeicoes Component', () => {
  it('should render meal registration form', () => {
    render(<RegistroRefeicoes />)
    
    expect(screen.getByLabelText(/tipo da refeição/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/descrição/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /registrar/i })).toBeInTheDocument()
  })

  it('should submit meal data', async () => {
    const mockAdicionarRefeicao = jest.fn()
    
    // Re-mock com função spy
    jest.doMock('../../stores/alimentacaoStore', () => ({
      useAlimentacaoStore: () => ({
        refeicoes: [],
        isLoading: false,
        error: null,
        adicionarRefeicao: mockAdicionarRefeicao,
        loadRefeicoes: jest.fn()
      })
    }))

    render(<RegistroRefeicoes />)
    
    fireEvent.change(screen.getByLabelText(/tipo da refeição/i), {
      target: { value: 'almoço' }
    })
    
    fireEvent.change(screen.getByLabelText(/descrição/i), {
      target: { value: 'Arroz e feijão' }
    })
    
    fireEvent.click(screen.getByRole('button', { name: /registrar/i }))
    
    await waitFor(() => {
      expect(mockAdicionarRefeicao).toHaveBeenCalledWith({
        tipo: 'almoço',
        descricao: 'Arroz e feijão',
        data: expect.any(String)
      })
    })
  })
})
```

## 📋 FASE 2: Validação da SATI

### 2.1 **Testes da Integração Maritaca AI**

#### A. Teste de Conectividade
```typescript
// test/sati/maritacaClient.test.ts
import { MaritacaClient } from '../../lib/sati/maritacaClient'

describe('Maritaca AI Integration', () => {
  let client: MaritacaClient

  beforeEach(() => {
    client = new MaritacaClient(process.env.MARITACA_API_KEY!)
  })

  it('should connect to Maritaca API', async () => {
    const response = await client.completion([
      { role: 'user', content: 'Olá!' }
    ])

    expect(response.choices).toBeDefined()
    expect(response.choices[0].message.content).toBeTruthy()
  }, 10000) // 10s timeout

  it('should generate embeddings', async () => {
    const embedding = await client.generateEmbedding('Teste de embedding')

    expect(Array.isArray(embedding)).toBe(true)
    expect(embedding.length).toBeGreaterThan(0)
    expect(typeof embedding[0]).toBe('number')
  }, 10000)

  it('should handle API errors gracefully', async () => {
    const invalidClient = new MaritacaClient('invalid-key')

    await expect(
      invalidClient.completion([{ role: 'user', content: 'test' }])
    ).rejects.toThrow()
  })
})
```

#### B. Teste do Sistema RAG
```typescript
// test/sati/ragSystem.test.ts
import { EmbeddingService } from '../../lib/sati/embeddingService'
import { ContextService } from '../../lib/sati/contextService'

describe('RAG System', () => {
  let embeddingService: EmbeddingService
  let contextService: ContextService

  beforeEach(() => {
    embeddingService = new EmbeddingService(process.env.MARITACA_API_KEY!)
    contextService = new ContextService(embeddingService)
  })

  it('should index user data', async () => {
    await embeddingService.indexUserData('test-user-id')
    
    // Verificar se dados foram indexados
    const results = await embeddingService.searchSimilar(
      'alimentação',
      'test-user-id'
    )

    expect(Array.isArray(results)).toBe(true)
  }, 30000)

  it('should build context for queries', async () => {
    const context = await contextService.buildContext(
      'test-user-id',
      'Como está minha alimentação?'
    )

    expect(context.userPreferences).toBeDefined()
    expect(context.relevantData).toBeDefined()
    expect(Array.isArray(context.relevantData)).toBe(true)
  })

  it('should find relevant documents', async () => {
    const results = await embeddingService.searchSimilar(
      'estudos matemática',
      'test-user-id',
      3
    )

    expect(results.length).toBeLessThanOrEqual(3)
    if (results.length > 0) {
      expect(results[0]).toHaveProperty('content')
      expect(results[0]).toHaveProperty('similarity')
    }
  })
})
```

### 2.2 **Teste do Serviço Principal SATI**

```typescript
// test/sati/satiService.test.ts
import { SatiService } from '../../lib/sati/satiService'

describe('SATI Service', () => {
  let satiService: SatiService

  beforeEach(() => {
    satiService = new SatiService(process.env.MARITACA_API_KEY!)
  })

  it('should process user messages', async () => {
    const response = await satiService.processMessage({
      message: 'Olá, como você pode me ajudar?'
    }, 'test-user-id')

    expect(response.message).toBeTruthy()
    expect(response.conversationId).toBeTruthy()
    expect(response.messageId).toBeTruthy()
  }, 15000)

  it('should maintain conversation context', async () => {
    // Primeira mensagem
    const response1 = await satiService.processMessage({
      message: 'Meu nome é João'
    }, 'test-user-id')

    // Segunda mensagem usando o mesmo contexto
    const response2 = await satiService.processMessage({
      message: 'Qual é o meu nome?',
      conversationId: response1.conversationId
    }, 'test-user-id')

    expect(response2.message.toLowerCase()).toContain('joão')
  }, 20000)

  it('should generate relevant suggestions', async () => {
    const response = await satiService.processMessage({
      message: 'Estou com dificuldade para estudar'
    }, 'test-user-id')

    expect(response.suggestions).toBeDefined()
    expect(Array.isArray(response.suggestions)).toBe(true)
    expect(response.suggestions!.length).toBeGreaterThan(0)
  }, 15000)
})
```

## 📋 FASE 3: Testes de Performance

### 3.1 **Benchmarks de Performance**

#### A. Teste de Performance do Supabase
```typescript
// test/performance/supabase.perf.test.ts
import { performance } from 'perf_hooks'
import { supabase } from '../../lib/supabase/client'

describe('Supabase Performance', () => {
  it('should load user data quickly', async () => {
    const start = performance.now()
    
    const { data, error } = await supabase
      .from('user_preferences')
      .select('*')
      .eq('user_id', 'test-user-id')
    
    const end = performance.now()
    const duration = end - start

    expect(error).toBeNull()
    expect(duration).toBeLessThan(2000) // Menos de 2 segundos
  })

  it('should handle concurrent requests', async () => {
    const start = performance.now()
    
    const promises = Array.from({ length: 10 }, () =>
      supabase
        .from('refeicoes')
        .select('*')
        .eq('user_id', 'test-user-id')
    )

    const results = await Promise.all(promises)
    
    const end = performance.now()
    const duration = end - start

    expect(results.every(r => !r.error)).toBe(true)
    expect(duration).toBeLessThan(5000) // Menos de 5 segundos para 10 requests
  })
})
```

#### B. Teste de Performance da SATI
```typescript
// test/performance/sati.perf.test.ts
import { performance } from 'perf_hooks'
import { SatiService } from '../../lib/sati/satiService'

describe('SATI Performance', () => {
  let satiService: SatiService

  beforeEach(() => {
    satiService = new SatiService(process.env.MARITACA_API_KEY!)
  })

  it('should respond within acceptable time', async () => {
    const start = performance.now()
    
    const response = await satiService.processMessage({
      message: 'Como posso melhorar minha produtividade?'
    }, 'test-user-id')
    
    const end = performance.now()
    const duration = end - start

    expect(response.message).toBeTruthy()
    expect(duration).toBeLessThan(10000) // Menos de 10 segundos
  }, 15000)

  it('should handle multiple conversations efficiently', async () => {
    const start = performance.now()
    
    const promises = Array.from({ length: 3 }, (_, i) =>
      satiService.processMessage({
        message: `Pergunta ${i + 1}`
      }, 'test-user-id')
    )

    const results = await Promise.all(promises)
    
    const end = performance.now()
    const duration = end - start

    expect(results.every(r => r.message)).toBe(true)
    expect(duration).toBeLessThan(30000) // Menos de 30 segundos para 3 requests
  }, 45000)
})
```

### 3.2 **Monitoramento de Recursos**

```typescript
// test/performance/resources.test.ts
describe('Resource Usage', () => {
  it('should not exceed memory limits', async () => {
    const initialMemory = process.memoryUsage().heapUsed
    
    // Executar operações que consomem memória
    for (let i = 0; i < 100; i++) {
      await satiService.processMessage({
        message: `Test message ${i}`
      }, 'test-user-id')
    }
    
    const finalMemory = process.memoryUsage().heapUsed
    const memoryIncrease = finalMemory - initialMemory
    
    // Verificar se o aumento de memória é aceitável (menos de 100MB)
    expect(memoryIncrease).toBeLessThan(100 * 1024 * 1024)
  })
})
```

## 📋 FASE 4: Testes de Segurança

### 4.1 **Validação RLS (Row Level Security)**

```typescript
// test/security/rls.test.ts
import { supabase } from '../../lib/supabase/client'

describe('Row Level Security', () => {
  it('should prevent access to other users data', async () => {
    // Tentar acessar dados de outro usuário
    const { data, error } = await supabase
      .from('user_preferences')
      .select('*')
      .eq('user_id', 'other-user-id')

    // Deve retornar vazio ou erro, nunca dados de outro usuário
    expect(data?.length || 0).toBe(0)
  })

  it('should allow access to own data only', async () => {
    // Configurar usuário autenticado
    await supabase.auth.signInWithPassword({
      email: 'test@example.com',
      password: 'testpassword'
    })

    const { data: { user } } = await supabase.auth.getUser()
    
    if (user) {
      const { data, error } = await supabase
        .from('user_preferences')
        .select('*')
        .eq('user_id', user.id)

      expect(error).toBeNull()
      // Deve retornar apenas dados do usuário autenticado
      expect(data?.every(item => item.user_id === user.id)).toBe(true)
    }
  })
})
```

### 4.2 **Validação de Sanitização**

```typescript
// test/security/sanitization.test.ts
describe('Input Sanitization', () => {
  it('should sanitize SQL injection attempts', async () => {
    const maliciousInput = "'; DROP TABLE users; --"
    
    await expect(
      satiService.processMessage({
        message: maliciousInput
      }, 'test-user-id')
    ).not.toThrow()
  })

  it('should sanitize XSS attempts', async () => {
    const xssInput = '<script>alert("xss")</script>'
    
    const response = await satiService.processMessage({
      message: xssInput
    }, 'test-user-id')

    expect(response.message).not.toContain('<script>')
  })
})
```

## 📋 FASE 5: Testes End-to-End

### 5.1 **Fluxos Completos de Usuário**

```typescript
// test/e2e/userFlows.test.ts
import { chromium } from 'playwright'

describe('User Flows E2E', () => {
  let browser: any
  let page: any

  beforeAll(async () => {
    browser = await chromium.launch()
    page = await browser.newPage()
  })

  afterAll(async () => {
    await browser.close()
  })

  it('should complete meal registration flow', async () => {
    await page.goto('http://localhost:3000/alimentacao')
    
    // Registrar uma refeição
    await page.fill('[data-testid="tipo-refeicao"]', 'almoço')
    await page.fill('[data-testid="descricao-refeicao"]', 'Arroz, feijão, carne')
    await page.click('[data-testid="registrar-refeicao"]')
    
    // Verificar se apareceu na lista
    await page.waitForSelector('[data-testid="lista-refeicoes"]')
    const meals = await page.textContent('[data-testid="lista-refeicoes"]')
    expect(meals).toContain('Arroz, feijão, carne')
  })

  it('should complete SATI conversation flow', async () => {
    await page.goto('http://localhost:3000/sati')
    
    // Enviar mensagem para SATI
    await page.fill('[data-testid="sati-input"]', 'Como está minha alimentação hoje?')
    await page.click('[data-testid="sati-send"]')
    
    // Aguardar resposta
    await page.waitForSelector('[data-testid="sati-response"]', { timeout: 15000 })
    const response = await page.textContent('[data-testid="sati-response"]')
    expect(response).toBeTruthy()
    expect(response!.length).toBeGreaterThan(10)
  })
})
```

## 📋 Checklist Final de Validação

### ✅ Migração Supabase:
- [ ] Todas as stores conectando corretamente
- [ ] CRUD operations funcionando
- [ ] RLS implementado e testado
- [ ] Performance aceitável (< 2s para queries simples)
- [ ] Realtime sync funcionando
- [ ] Error handling implementado
- [ ] Backward compatibility mantida

### ✅ Implementação SATI:
- [ ] Conexão Maritaca AI estável
- [ ] Sistema RAG indexando dados
- [ ] Respostas contextualizadas
- [ ] Interface chat funcional
- [ ] Performance aceitável (< 10s para respostas)
- [ ] Tratamento de erros robusto
- [ ] Segurança implementada

### ✅ Qualidade Geral:
- [ ] Build passando sem erros
- [ ] Testes automatizados passando (>80% cobertura)
- [ ] Testes E2E funcionando
- [ ] Performance dentro dos limites
- [ ] Segurança validada
- [ ] Documentação atualizada

## 🚨 Comandos de Validação para LLM

### Execução de Testes:
```bash
# Testes básicos
npm run test                    # Todos os testes
npm run test:unit              # Testes unitários
npm run test:integration       # Testes de integração
npm run test:e2e              # Testes end-to-end

# Testes específicos
npm run test:supabase         # Validação Supabase
npm run test:sati             # Validação SATI
npm run test:performance      # Testes de performance
npm run test:security         # Testes de segurança

# Build e lint
npm run build                 # Build de produção
npm run type-check           # Verificação de tipos
npm run lint                 # Linting
```

### Validação Manual:
```bash
# Ambiente de desenvolvimento
npm run dev                   # Iniciar servidor

# Testar no browser:
# - http://localhost:3000/alimentacao
# - http://localhost:3000/sati
# - Verificar funcionamento de cada feature
```

---

**Anterior:** [05 - Implementação SATI](./05-implementacao-sati.md) | **Próximo:** [07 - Checklist de Execução](./07-checklist-execucao.md)
