# 02 - Pré-requisitos e Configuração Inicial

## 🔧 Ambiente de Desenvolvimento

### 1. **Verificações Iniciais**

#### A. Análise do Projeto Atual
```bash
# Execute estas verificações primeiro
□ Verificar Node.js version (>=18)
□ Verificar npm/yarn funcionando
□ Testar build atual: npm run build
□ Verificar testes existentes: npm test
□ Confirmar funcionamento no browser
```

#### B. Dependências do Projeto
```typescript
// Verificar se estas dependências estão instaladas
- next: "^14.x"
- react: "^18.x"
- zustand: "^4.x"
- tailwindcss: "^3.x"
- typescript: "^5.x"
```

### 2. **Configuração Supabase**

#### A. Conta e Projeto
```bash
# Passos obrigatórios
1. Criar conta no Supabase (se não existir)
2. Criar novo projeto
3. Anotar URL e anon key
4. Configurar variáveis de ambiente
```

#### B. Variáveis de Ambiente
```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# .env.example (template)
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
MARITACA_API_KEY=
```

### 3. **Configuração Maritaca AI**

#### A. Conta e API Key
```bash
# Configuração necessária
1. Criar conta na Maritaca AI
2. Obter API key para Sabiá 3
3. Configurar rate limits
4. Testar conectividade
```

#### B. Configuração de Teste
```typescript
// Arquivo de teste da API
// test/maritaca-connection.test.ts
import { MaritacaAI } from '../lib/maritaca'

describe('Maritaca AI Connection', () => {
  it('should connect successfully', async () => {
    const client = new MaritacaAI(process.env.MARITACA_API_KEY)
    const response = await client.testConnection()
    expect(response.status).toBe('ok')
  })
})
```

## 📁 Estrutura de Arquivos para Migração

### 1. **Backup e Versionamento**

#### A. Criar Branch de Migração
```bash
# Git workflow recomendado
git checkout -b migration/supabase-sati
git add .
git commit -m "Backup before migration"
```

#### B. Estrutura de Backup
```
/backup/
  ├── stores/           # Backup das stores originais
  ├── components/       # Componentes que serão modificados
  ├── lib/             # Utilitários atuais
  └── package.json     # Dependências atuais
```

### 2. **Nova Estrutura para Supabase**

#### A. Diretórios Obrigatórios
```
/lib/
  ├── supabase/
  │   ├── client.ts        # Cliente Supabase
  │   ├── auth.ts          # Funções de autenticação
  │   ├── database.ts      # Operações CRUD
  │   └── types.ts         # Tipos TypeScript
  ├── stores/
  │   ├── base/
  │   │   └── useStore.ts  # Store base com Supabase
  │   └── [existing stores] # Stores migradas
  └── sati/
      ├── client.ts        # Cliente SATI
      ├── rag.ts          # Sistema RAG
      └── types.ts        # Tipos da SATI
```

#### B. Configurações Necessárias
```typescript
// lib/supabase/client.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

## 🔍 Análise Obrigatória Pré-Migração

### 1. **Mapeamento de Stores Existentes**

#### A. Lista de Stores para Migração
```bash
# Use semantic_search para encontrar todas as stores
□ alimentacaoStore.ts
□ autoconhecimentoStore.ts
□ concursosStore.ts
□ estudosStore.ts
□ simuladoStore.ts
□ perfilStore.ts
□ sonoStore.ts
□ pomodoroStore.ts
□ [outras identificadas]
```

#### B. Análise de Dependências
```typescript
// Para cada store, mapear:
interface StoreAnalysis {
  name: string
  dataTypes: string[]        // Tipos de dados armazenados
  dependencies: string[]     // Outras stores usadas
  components: string[]       // Componentes que usam
  complexity: 'low' | 'medium' | 'high'
  migrationPriority: number  // 1-10 (1 = primeiro)
}
```

### 2. **Análise de Componentes**

#### A. Componentes que Usam Stores
```bash
# Usar grep_search para encontrar
- Componentes que importam stores
- Hooks personalizados
- Páginas que dependem de dados
```

#### B. Pontos de Integração
```typescript
// Identificar onde stores são usadas
- Formulários de entrada de dados
- Listas e visualizações
- Componentes de estado
- Hooks de sincronização
```

## 🚀 Instalação de Dependências

### 1. **Dependências Supabase**
```bash
npm install @supabase/supabase-js
npm install @supabase/auth-helpers-nextjs
npm install @supabase/auth-helpers-react
```

### 2. **Dependências SATI/IA**
```bash
# Para integração com Maritaca AI
npm install axios
npm install openai  # Para compatibilidade de tipos
npm install langchain  # Para RAG system
```

### 3. **Dependências de Desenvolvimento**
```bash
npm install -D @types/node
npm install -D supabase  # CLI para migrations
```

## ✅ Checklist de Pré-requisitos

### Antes de Começar a Migração:

#### Ambiente:
- [ ] Node.js >=18 instalado
- [ ] Projeto atual buildando sem erros
- [ ] Todos os testes passando
- [ ] Backup do código atual realizado
- [ ] Branch de migração criada

#### Supabase:
- [ ] Conta Supabase criada
- [ ] Projeto Supabase criado
- [ ] Variáveis de ambiente configuradas
- [ ] Conectividade testada
- [ ] CLI Supabase instalado

#### Maritaca AI:
- [ ] Conta Maritaca criada
- [ ] API key obtida
- [ ] Rate limits compreendidos
- [ ] Teste de conectividade realizado
- [ ] Documentação API revisada

#### Código:
- [ ] Todas as stores mapeadas
- [ ] Dependências entre stores identificadas
- [ ] Componentes que usam stores listados
- [ ] Prioridade de migração definida
- [ ] Estrutura de arquivos planejada

#### Ferramentas:
- [ ] Dependências Supabase instaladas
- [ ] Dependências IA instaladas
- [ ] Tipos TypeScript configurados
- [ ] Ferramentas de teste preparadas
- [ ] Linting e formatação funcionando

## 🚨 Verificações Críticas

### Antes de Prosseguir:

```bash
# Execute estes comandos
npm run build    # Deve passar sem erros
npm run lint     # Deve passar sem avisos críticos
npm test         # Testes existentes devem passar
npm start        # Aplicação deve iniciar
```

### Validações de Ambiente:
```typescript
// Teste estas variáveis
console.log('Supabase URL:', process.env.NEXT_PUBLIC_SUPABASE_URL)
console.log('Supabase Key:', process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ? 'OK' : 'MISSING')
console.log('Maritaca Key:', process.env.MARITACA_API_KEY ? 'OK' : 'MISSING')
```

## 📋 Troubleshooting Pré-requisitos

### Problemas Comuns:

#### 1. Build Falhando
```bash
# Soluções típicas
- Verificar versão Node.js
- Limpar cache: npm cache clean --force
- Reinstalar dependências: rm -rf node_modules && npm install
- Verificar types: npm run type-check
```

#### 2. Conectividade Supabase
```bash
# Teste de conectividade
npx supabase status
npx supabase test
```

#### 3. Variáveis de Ambiente
```bash
# Verificar se estão sendo carregadas
- Reiniciar servidor de desenvolvimento
- Verificar nome do arquivo (.env.local)
- Confirmar sintaxe das variáveis
```

---

**Anterior:** [01 - Abordagem Geral](./01-abordagem-geral.md) | **Próximo:** [03 - Análise do Contexto](./03-analise-contexto.md)
