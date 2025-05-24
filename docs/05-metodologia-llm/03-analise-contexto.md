# 03 - Análise do Contexto Atual

## 🔍 Estratégia de Análise para LLM

### Objetivo:
Compreender completamente a estrutura atual do código antes de iniciar qualquer migração.

### Princípio:
**"Analise primeiro, modifique depois"** - Nunca altere código sem entender completamente seu contexto e dependências.

## 📊 Roteiro de Análise Sequencial

### 1. **Análise da Estrutura Geral**

#### A. Mapeamento da Arquitetura Atual
```typescript
// Execute estes comandos na ordem:
1. list_dir(/workspaces/stayfocus-aug) // Estrutura raiz
2. semantic_search("store") // Encontrar todas as stores
3. grep_search("import.*Store") // Dependências entre stores
4. file_search("**/*.ts") // Todos arquivos TypeScript
```

#### B. Identificação de Padrões
```typescript
// Procurar por:
- Padrões de importação de stores
- Hooks personalizados (use*)
- Contextos React
- Tipos TypeScript compartilhados
- Utilitários comuns
```

### 2. **Análise Detalhada das Stores**

#### A. Lista de Stores Identificadas
Para cada store encontrada, executar análise completa:

```typescript
// Template de análise por store:
interface StoreAnalysis {
  fileName: string
  location: string
  imports: string[]           // O que ela importa
  exports: string[]          // O que ela exporta
  stateShape: object         // Formato do estado
  actions: string[]          // Métodos disponíveis
  dependencies: string[]     // Outras stores usadas
  usedBy: string[]          // Componentes que a usam
  dataTypes: string[]       // Tipos de dados armazenados
  persistance: boolean      // Se usa persist/localStorage
  complexity: 'low'|'medium'|'high'
}
```

#### B. Stores Prioritárias para Análise:

1. **alimentacaoStore.ts** - Dados de refeições e hidratação
2. **autoconhecimentoStore.ts** - Notas e categorias
3. **concursosStore.ts** - Concursos e questões
4. **estudosStore.ts** - Registros de estudo
5. **simuladoStore.ts** - Simulados e histórico
6. **perfilStore.ts** - Dados do usuário

### 3. **Comandos de Análise para LLM**

#### A. Para Cada Store:
```bash
# 1. Ler conteúdo completo
read_file(/path/to/store.ts, 0, -1)

# 2. Buscar onde é usada
grep_search("import.*NomeStore", includePattern="**/*.{ts,tsx}")

# 3. Buscar referências
semantic_search("NomeStore")

# 4. Verificar tipos relacionados
grep_search("interface.*Nome", includePattern="**/*.ts")
```

#### B. Para Dependências:
```bash
# 1. Mapear imports
grep_search("from ['\"].*store", includePattern="**/*.ts")

# 2. Buscar hooks relacionados
semantic_search("useStore use*")

# 3. Verificar tipos compartilhados
file_search("**/types/**/*.ts")
```

## 🗺️ Mapeamento de Dependências

### 1. **Matriz de Dependências**

```typescript
// Criar matriz de quem depende de quem:
interface DependencyMatrix {
  [storeName: string]: {
    imports: string[]      // Stores que esta store importa
    importedBy: string[]   // Stores que importam esta store
    components: string[]   // Componentes que usam
    weight: number        // Peso da dependência (1-10)
  }
}
```

### 2. **Ordem de Migração Recomendada**

#### A. Stores Independentes (Migrar Primeiro):
- Stores sem dependências de outras stores
- Dados simples e auto-contidos
- Menor impacto se algo der errado

#### B. Stores com Dependências Baixas:
- Dependem apenas de stores já migradas
- Complexidade moderada
- Impacto controlado

#### C. Stores Complexas (Migrar Por Último):
- Múltiplas dependências
- Lógica complexa de estado
- Alto impacto em caso de erro

## 📋 Template de Análise por Store

### Para cada store, documentar:

```markdown
## [Nome da Store] Analysis

### 📍 Localização
- **Arquivo:** /path/to/store.ts
- **Tamanho:** X linhas
- **Última modificação:** [data]

### 🔗 Dependências
- **Importa stores:** [lista]
- **Importa utils:** [lista]
- **Tipos usado:** [lista]

### 📊 Estado
```typescript
interface StoreState {
  // Documentar formato do estado
}
```

### ⚙️ Ações
- `action1()` - Descrição
- `action2(param)` - Descrição
- `action3()` - Descrição

### 🎯 Componentes que Usam
- Component1 (/path/to/component1.tsx)
- Component2 (/path/to/component2.tsx)

### 📈 Complexidade de Migração
- **Nível:** Low/Medium/High
- **Razão:** [explicação]
- **Estimativa:** X horas
- **Riscos:** [lista de riscos]

### 🗄️ Estrutura de Dados Supabase
```sql
-- Schema SQL necessário
CREATE TABLE nome_tabela (
  -- campos necessários
);
```

### ✅ Critérios de Validação
- [ ] Estado migrado corretamente
- [ ] Ações funcionando
- [ ] Componentes não quebrados
- [ ] Performance mantida
```

## 🔧 Comandos Específicos para Análise

### 1. **Análise de alimentacaoStore**
```bash
# Localizar e analisar
semantic_search("alimentacao refeicao hidratacao")
read_file(/app/stores/alimentacaoStore.ts, 0, -1)
grep_search("alimentacaoStore", includePattern="**/*.{ts,tsx}")
```

### 2. **Análise de autoconhecimentoStore**
```bash
# Localizar e analisar
semantic_search("autoconhecimento notas categoria")
read_file(/app/stores/autoconhecimentoStore.ts, 0, -1)
grep_search("autoconhecimentoStore", includePattern="**/*.{ts,tsx}")
```

### 3. **Análise de concursosStore**
```bash
# Localizar e analisar
semantic_search("concurso questao simulado")
read_file(/app/stores/concursosStore.ts, 0, -1)
grep_search("concursosStore", includePattern="**/*.{ts,tsx}")
```

## 📊 Análise de Componentes

### 1. **Componentes Críticos**

#### A. Componentes de Formulário:
```bash
# Buscar componentes que coletam dados
semantic_search("form input useState")
grep_search("onSubmit", includePattern="**/*.tsx")
```

#### B. Componentes de Listagem:
```bash
# Buscar componentes que mostram dados
semantic_search("map list data")
grep_search("\.map\(", includePattern="**/*.tsx")
```

### 2. **Hooks Personalizados**
```bash
# Encontrar hooks que usam stores
semantic_search("use* hook custom")
grep_search("export.*use[A-Z]", includePattern="**/*.ts")
```

## ⚠️ Pontos de Atenção Críticos

### 1. **Persistência de Dados**
```typescript
// Verificar se stores usam persist
grep_search("persist.*storage", includePattern="**/*.ts")
```

### 2. **Estado Complexo**
```typescript
// Identificar estados aninhados
semantic_search("nested object deep")
grep_search("\..*\.", includePattern="**/stores/*.ts")
```

### 3. **Side Effects**
```typescript
// Buscar efeitos colaterais
semantic_search("useEffect setTimeout setInterval")
grep_search("useEffect|setTimeout|setInterval", includePattern="**/*.ts")
```

## 📋 Checklist de Análise Completa

### Antes de Migrar:
- [ ] Todas as stores identificadas e analisadas
- [ ] Matriz de dependências criada
- [ ] Ordem de migração definida
- [ ] Componentes mapeados
- [ ] Hooks personalizados identificados
- [ ] Pontos de persistência localizados
- [ ] Estados complexos documentados
- [ ] Side effects mapeados
- [ ] Critérios de validação definidos
- [ ] Riscos identificados e mitigados

### Documentação Criada:
- [ ] Análise individual de cada store
- [ ] Mapa de dependências visual
- [ ] Plano de migração sequencial
- [ ] Lista de componentes afetados
- [ ] Schema SQL preliminar
- [ ] Testes de validação planejados

## 🚀 Próximos Passos

Após completar a análise:

1. **Revisar documentação** gerada
2. **Validar ordem de migração** planejada
3. **Preparar ambiente Supabase** com base na análise
4. **Iniciar migração** pela store mais simples
5. **Validar cada etapa** antes de prosseguir

---

**Anterior:** [02 - Pré-requisitos](./02-pre-requisitos.md) | **Próximo:** [04 - Migração Supabase](./04-migracao-supabase.md)
