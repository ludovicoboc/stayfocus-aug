# Análise da Estrutura Atual das Stores

## Objetivo
Compreender a estrutura atual das stores para identificar entidades e relacionamentos.

## Mapeamento das Entidades e Campos

### 1. Alimentação
**Store**: `alimentacaoStore.ts`
**Entidades**:
- **Refeicao**:
  - id: string
  - horario: string
  - descricao: string

- **RegistroRefeicao**:
  - id: string
  - data: string
  - horario: string
  - descricao: string
  - tipoIcone: string | null
  - foto: string | null

- **Hidratação** (não é uma entidade separada, mas parte do estado):
  - coposBebidos: number
  - metaDiaria: number
  - ultimoRegistro: string | null

### 2. Atividades
**Store**: `atividadesStore.ts`
**Entidades**:
- **Atividade**:
  - id: string
  - nome: string
  - categoria: string
  - duracao: number (em minutos)
  - observacoes: string
  - data: string
  - concluida: boolean

### 3. Autoconhecimento
**Store**: `autoconhecimentoStore.ts`
**Entidades**:
- **Nota**:
  - id: string
  - titulo: string
  - conteudo: string
  - secao: 'quem-sou' | 'meus-porques' | 'meus-padroes'
  - tags: string[]
  - dataCriacao: string
  - dataAtualizacao: string
  - imagemUrl?: string

### 4. Concursos
**Store**: `concursosStore.ts`
**Entidades**:
- **Concurso**:
  - id: string
  - titulo: string
  - organizadora: string
  - dataInscricao: string
  - dataProva: string
  - edital?: string
  - status: 'planejado' | 'inscrito' | 'estudando' | 'realizado' | 'aguardando_resultado'
  - conteudoProgramatico: ConteudoProgramatico[]

- **ConteudoProgramatico**:
  - disciplina: string
  - topicos: string[]
  - progresso: number

### 5. Finanças
**Store**: `financasStore.ts`
**Entidades**:
- **Categoria**:
  - id: string
  - nome: string
  - cor: string
  - icone: string

- **Transacao**:
  - id: string
  - data: string
  - valor: number
  - descricao: string
  - categoriaId: string
  - tipo: 'receita' | 'despesa'

- **Envelope**:
  - id: string
  - nome: string
  - cor: string
  - valorAlocado: number
  - valorUtilizado: number

- **PagamentoRecorrente**:
  - id: string
  - descricao: string
  - valor: number
  - dataVencimento: string
  - categoriaId: string
  - proximoPagamento: string | null
  - pago: boolean

### 6. Hiperfocos
**Store**: `hiperfocosStore.ts`
**Entidades**:
- **Hiperfoco**:
  - id: string
  - titulo: string
  - descricao: string
  - tarefas: Tarefa[]
  - subTarefas: Record<string, Tarefa[]>
  - cor: string
  - dataCriacao: string
  - tempoLimite?: number

- **Tarefa** (dentro do hiperfoco):
  - id: string
  - texto: string
  - concluida: boolean
  - cor?: string

- **SessaoAlternancia**:
  - id: string
  - titulo: string
  - hiperfocoAtual: string | null
  - hiperfocoAnterior: string | null
  - tempoInicio: string
  - duracaoEstimada: number
  - concluida: boolean

### 7. Histórico de Simulados
**Store**: `historicoSimuladosStore.ts`
**Entidades**:
- **SimuladoHistoricoEntry**:
  - titulo: string
  - totalQuestoes: number
  - tentativas: Tentativa[]

- **Tentativa**:
  - timestamp: string
  - acertos: number
  - percentual: number

### 8. Painel do Dia
**Store**: `painelDiaStore.ts`
**Entidades**:
- **BlocoTempo**:
  - id: string
  - hora: string
  - atividade: string
  - categoria: 'inicio' | 'alimentacao' | 'estudos' | 'saude' | 'lazer' | 'nenhuma'

### 9. Perfil
**Store**: `perfilStore.ts`
**Entidades**:
- **PreferenciasVisuais**:
  - altoContraste: boolean
  - reducaoEstimulos: boolean
  - textoGrande: boolean

- **MetasDiarias**:
  - horasSono: number
  - tarefasPrioritarias: number
  - coposAgua: number
  - pausasProgramadas: number

### 10. Pomodoro
**Store**: `pomodoroStore.ts`
**Entidades**:
- **ConfiguracaoPomodoro**:
  - tempoFoco: number
  - tempoPausa: number
  - tempoLongapausa: number
  - ciclosAntesLongapausa: number

### 11. Prioridades
**Store**: `prioridadesStore.ts`
**Entidades**:
- **Prioridade**:
  - id: string
  - texto: string
  - concluida: boolean
  - data: string
  - tipo?: 'geral' | 'concurso'
  - origemId?: string

### 12. Questões
**Store**: `questoesStore.ts`
**Entidades**:
- **Questao**:
  - id: string
  - concursoId?: string
  - disciplina: string
  - topico: string
  - enunciado: string
  - alternativas: Alternativa[]
  - respostaCorreta: string
  - justificativa?: string
  - nivelDificuldade?: 'facil' | 'medio' | 'dificil'
  - ano?: number
  - banca?: string
  - tags?: string[]
  - respondida?: boolean
  - respostaUsuario?: string
  - acertou?: boolean

- **Alternativa**:
  - id: string
  - texto: string
  - correta: boolean

### 13. Receitas
**Store**: `receitasStore.ts`
**Entidades**:
- **Receita**:
  - id: string
  - nome: string
  - descricao: string
  - categorias: string[]
  - tags: string[]
  - tempoPreparo: number
  - porcoes: number
  - calorias: string
  - imagem: string
  - ingredientes: Ingrediente[]
  - passos: string[]

- **Ingrediente**:
  - nome: string
  - quantidade: number
  - unidade: string

### 14. Registro de Estudos
**Store**: `registroEstudosStore.ts`
**Entidades**:
- **SessaoEstudo**:
  - id: string
  - titulo: string
  - descricao: string
  - duracao: number
  - data: string
  - completo: boolean

### 15. Simulado
**Store**: `simuladoStore.ts`
**Entidades**:
- **SimuladoMetadata**:
  - titulo: string
  - concurso?: string
  - ano?: number
  - area?: string
  - nivel?: string
  - totalQuestoes: number
  - tempoPrevisto?: number
  - autor?: string
  - dataGeracao?: string

- **Questao** (específica para simulado):
  - id: number
  - enunciado: string
  - alternativas: { [key: string]: string }
  - gabarito: string
  - assunto?: string
  - dificuldade?: number
  - dicas?: string[]
  - explicacao?: string

### 16. Sono
**Store**: `sonoStore.ts`
**Entidades**:
- **RegistroSono**:
  - id: string
  - inicio: string
  - fim: string | null
  - qualidade: number | null
  - notas: string

- **ConfiguracaoLembrete**:
  - id: string
  - tipo: 'dormir' | 'acordar'
  - horario: string
  - diasSemana: number[]
  - ativo: boolean

### 17. Sugestões
**Store**: `sugestoesStore.ts`
**Entidades**:
- Não possui entidades complexas, apenas um array de strings (sugestoesFavoritas)

## Relacionamentos entre Entidades

1. **Concursos e Questões**:
   - Questões podem estar vinculadas a um concurso específico através do campo `concursoId` na entidade Questao.

2. **Concursos e Prioridades**:
   - Prioridades podem estar vinculadas a um concurso através dos campos `tipo: 'concurso'` e `origemId` (que armazena o ID do concurso).

3. **Hiperfocos e Tarefas**:
   - Hiperfocos contêm uma lista de tarefas e subtarefas.
   - Subtarefas estão vinculadas a tarefas pai através de um mapa (Record<string, Tarefa[]>).

4. **Finanças - Categorias e Transações**:
   - Transações estão vinculadas a categorias através do campo `categoriaId`.

5. **Finanças - Categorias e Pagamentos Recorrentes**:
   - Pagamentos recorrentes estão vinculados a categorias através do campo `categoriaId`.

6. **Simulados e Histórico de Simulados**:
   - O histórico de simulados armazena informações sobre tentativas de simulados.

7. **Simulados e Questões**:
   - Simulados contêm questões, mas usam uma estrutura diferente da entidade Questao do questoesStore.

## Regras de Negócio Implícitas

1. **Alimentação**:
   - Limite de copos de água: entre 1 e 15 (ajustarMeta).
   - Registro de refeições requer horário e descrição.

2. **Finanças**:
   - Limite de 5 categorias de finanças.
   - Pagamentos recorrentes têm status de pagamento (pago/não pago).
   - Envelopes têm valores alocados e utilizados para controle de orçamento.

3. **Hiperfocos**:
   - Hiperfocos podem ter tempo limite opcional.
   - Sessões de alternância controlam a mudança entre hiperfocos.

4. **Pomodoro**:
   - Ciclo de trabalho seguido por pausas curtas e longas.
   - Pausa longa ocorre após um número específico de ciclos.

5. **Prioridades**:
   - Prioridades são organizadas por data.
   - Prioridades podem ser gerais ou vinculadas a concursos.

6. **Sono**:
   - Qualidade do sono é avaliada em uma escala de 1 a 5.
   - Lembretes podem ser configurados para dias específicos da semana.

7. **Perfil**:
   - Configurações de acessibilidade (alto contraste, texto grande).
   - Metas diárias para sono, tarefas, hidratação e pausas.

## Índices Necessários para Otimização

1. **Concursos**:
   - Índice em `status` para filtrar concursos por status.
   - Índice em `dataProva` para ordenar concursos por data.

2. **Questões**:
   - Índice em `concursoId` para buscar questões por concurso.
   - Índice em `disciplina` e `topico` para filtrar questões por assunto.
   - Índice em `tags` para busca por tags.

3. **Transações Financeiras**:
   - Índice em `data` para filtrar transações por período.
   - Índice em `categoriaId` para agrupar transações por categoria.
   - Índice em `tipo` para separar receitas e despesas.

4. **Registros de Sono**:
   - Índice em `inicio` para buscar registros por data.
   - Índice em `qualidade` para análises de qualidade do sono.

5. **Prioridades**:
   - Índice em `data` para filtrar prioridades por data.
   - Índice em `concluida` para filtrar tarefas concluídas/pendentes.
   - Índice em `tipo` e `origemId` para filtrar prioridades por origem.

6. **Hiperfocos**:
   - Índice em `dataCriacao` para ordenar hiperfocos por data.

7. **Sessões de Estudo**:
   - Índice em `data` para filtrar sessões por data.
   - Índice em `completo` para filtrar sessões completas/incompletas.

## Conclusão

A análise da estrutura atual das stores revela um sistema bem organizado com entidades claramente definidas e relacionamentos estabelecidos. O sistema utiliza o Zustand com persistência local para gerenciar o estado da aplicação, com cada store responsável por um domínio específico.

As principais entidades identificadas incluem Concursos, Questões, Finanças, Hiperfocos, Alimentação, Sono, entre outras, cada uma com seus próprios campos e tipos de dados. Os relacionamentos entre essas entidades são estabelecidos principalmente através de IDs de referência.

As regras de negócio implícitas incluem limitações em certos valores, requisitos de campos obrigatórios e lógica específica para cada domínio. Para otimização, seria útil implementar índices em campos frequentemente usados para filtragem, agrupamento e ordenação.

Esta análise fornece uma base sólida para entender a estrutura atual do sistema e pode ser usada para futuras melhorias, como a migração para um banco de dados relacional ou a implementação de novas funcionalidades.
