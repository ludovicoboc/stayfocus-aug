# Modelo Lógico do Banco de Dados - StayFocus

## Contextualização

Este documento apresenta o modelo lógico do banco de dados para o projeto StayFocus, desenvolvido como parte da Sprint 1, conforme solicitado na tarefa "Criar modelo lógico do banco de dados" do Scrum I. O modelo foi criado com base na análise da estrutura atual das stores (documentada em `scrum-I-I.md`) e nos requisitos especificados nos documentos `jira_sprints_1-3_infraestrutura.md` e `especif.md`.

O modelo lógico define as tabelas, colunas, chaves primárias, chaves estrangeiras, constraints e validações necessárias para implementar o banco de dados no Supabase, seguindo as melhores práticas de modelagem de dados.

## Modelo Lógico do Banco de Dados

### 1. Usuários e Preferências

```sql
-- Extensão da tabela de usuários do Supabase Auth
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  nome TEXT,
  email TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Preferências do usuário
CREATE TABLE user_preferences (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  alto_contraste BOOLEAN DEFAULT false,
  reducao_estimulos BOOLEAN DEFAULT false,
  texto_grande BOOLEAN DEFAULT false,
  modo_refugio BOOLEAN DEFAULT false,
  tema TEXT DEFAULT 'system',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT user_preferences_user_id_key UNIQUE (user_id)
);

-- Metas diárias do usuário
CREATE TABLE metas_diarias (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  tipo TEXT NOT NULL,
  valor INTEGER NOT NULL,
  ativa BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT metas_diarias_tipo_check CHECK (tipo IN ('sono', 'tarefas', 'hidratacao', 'pausas'))
);
```

### 2. Alimentação

```sql
-- Registro de refeições
CREATE TABLE refeicoes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  data TIMESTAMP WITH TIME ZONE NOT NULL,
  tipo TEXT NOT NULL,
  descricao TEXT NOT NULL,
  foto_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT refeicoes_descricao_not_empty CHECK (length(descricao) > 0)
);

-- Registro de hidratação
CREATE TABLE hidratacao (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  data TIMESTAMP WITH TIME ZONE NOT NULL,
  quantidade_ml INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT hidratacao_quantidade_check CHECK (quantidade_ml > 0)
);

-- Receitas
CREATE TABLE receitas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  nome TEXT NOT NULL,
  ingredientes JSONB NOT NULL,
  modo_preparo TEXT,
  tempo_preparo INTEGER,
  porcoes INTEGER,
  categorias TEXT[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT receitas_nome_not_empty CHECK (length(nome) > 0),
  CONSTRAINT receitas_tempo_preparo_check CHECK (tempo_preparo IS NULL OR tempo_preparo > 0),
  CONSTRAINT receitas_porcoes_check CHECK (porcoes IS NULL OR porcoes > 0)
);

-- Lista de compras
CREATE TABLE lista_compras (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  item TEXT NOT NULL,
  quantidade TEXT,
  unidade TEXT,
  comprado BOOLEAN DEFAULT false,
  receita_id UUID REFERENCES receitas(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT lista_compras_item_not_empty CHECK (length(item) > 0)
);
```

### 3. Autoconhecimento

```sql
-- Notas de autoconhecimento
CREATE TABLE notas_autoconhecimento (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  categoria TEXT NOT NULL,
  titulo TEXT NOT NULL,
  conteudo TEXT,
  tags TEXT[],
  imagem_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT notas_autoconhecimento_titulo_not_empty CHECK (length(titulo) > 0),
  CONSTRAINT notas_autoconhecimento_categoria_check CHECK (categoria IN ('quem_sou', 'meus_porques', 'meus_padroes', 'outros'))
);
```

### 4. Estudos

```sql
-- Concursos
CREATE TABLE concursos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  titulo TEXT NOT NULL,
  organizadora TEXT,
  data_inscricao TIMESTAMP WITH TIME ZONE,
  data_prova TIMESTAMP WITH TIME ZONE,
  edital TEXT,
  status TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT concursos_titulo_not_empty CHECK (length(titulo) > 0),
  CONSTRAINT concursos_status_check CHECK (status IN ('planejado', 'inscrito', 'estudando', 'realizado', 'aguardando_resultado'))
);

-- Conteúdo programático
CREATE TABLE conteudo_programatico (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  concurso_id UUID REFERENCES concursos(id) ON DELETE CASCADE,
  disciplina TEXT NOT NULL,
  topicos JSONB,
  progresso INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT conteudo_programatico_disciplina_not_empty CHECK (length(disciplina) > 0),
  CONSTRAINT conteudo_programatico_progresso_check CHECK (progresso BETWEEN 0 AND 100)
);

-- Sessões de estudo
CREATE TABLE sessoes_estudo (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  inicio TIMESTAMP WITH TIME ZONE NOT NULL,
  fim TIMESTAMP WITH TIME ZONE,
  duracao_minutos INTEGER,
  assunto TEXT,
  concurso_id UUID REFERENCES concursos(id) ON DELETE SET NULL,
  completo BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT sessoes_estudo_duracao_check CHECK (duracao_minutos IS NULL OR duracao_minutos > 0)
);

-- Simulados
CREATE TABLE simulados (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  titulo TEXT NOT NULL,
  total_questoes INTEGER NOT NULL,
  concurso_id UUID REFERENCES concursos(id) ON DELETE SET NULL,
  data_criacao TIMESTAMP WITH TIME ZONE DEFAULT now(),
  data_conclusao TIMESTAMP WITH TIME ZONE,
  personalizado BOOLEAN DEFAULT false,
  CONSTRAINT simulados_titulo_not_empty CHECK (length(titulo) > 0),
  CONSTRAINT simulados_total_questoes_check CHECK (total_questoes > 0)
);

-- Questões de simulado
CREATE TABLE questoes_simulado (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  simulado_id UUID REFERENCES simulados(id) ON DELETE CASCADE,
  enunciado TEXT NOT NULL,
  alternativas JSONB NOT NULL,
  gabarito TEXT NOT NULL,
  resposta_usuario TEXT,
  assunto TEXT,
  dificuldade TEXT,
  explicacao TEXT,
  ordem INTEGER,
  CONSTRAINT questoes_simulado_enunciado_not_empty CHECK (length(enunciado) > 0),
  CONSTRAINT questoes_simulado_gabarito_not_empty CHECK (length(gabarito) > 0),
  CONSTRAINT questoes_simulado_dificuldade_check CHECK (dificuldade IS NULL OR dificuldade IN ('facil', 'medio', 'dificil'))
);

-- Materiais do Drive
CREATE TABLE materiais_drive (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  tipo TEXT NOT NULL,
  folder_id TEXT NOT NULL,
  file_id TEXT,
  file_name TEXT,
  last_accessed TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT materiais_drive_tipo_not_empty CHECK (length(tipo) > 0),
  CONSTRAINT materiais_drive_folder_id_not_empty CHECK (length(folder_id) > 0)
);
```

### 5. Finanças

```sql
-- Categorias financeiras
CREATE TABLE categorias_financeiras (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  nome TEXT NOT NULL,
  cor TEXT NOT NULL,
  icone TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT categorias_financeiras_nome_not_empty CHECK (length(nome) > 0)
);

-- Transações financeiras
CREATE TABLE transacoes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  data TIMESTAMP WITH TIME ZONE NOT NULL,
  valor DECIMAL(10,2) NOT NULL,
  descricao TEXT NOT NULL,
  categoria_id UUID REFERENCES categorias_financeiras(id) ON DELETE SET NULL,
  tipo TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT transacoes_descricao_not_empty CHECK (length(descricao) > 0),
  CONSTRAINT transacoes_valor_check CHECK (valor > 0),
  CONSTRAINT transacoes_tipo_check CHECK (tipo IN ('receita', 'despesa'))
);

-- Envelopes
CREATE TABLE envelopes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  nome TEXT NOT NULL,
  orcamento DECIMAL(10,2) DEFAULT 0,
  saldo_atual DECIMAL(10,2) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT envelopes_nome_not_empty CHECK (length(nome) > 0),
  CONSTRAINT envelopes_orcamento_check CHECK (orcamento >= 0)
);

-- Pagamentos
CREATE TABLE pagamentos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  descricao TEXT NOT NULL,
  valor DECIMAL(10,2) NOT NULL,
  data_vencimento TIMESTAMP WITH TIME ZONE NOT NULL,
  recorrente BOOLEAN DEFAULT false,
  pago BOOLEAN DEFAULT false,
  categoria_id UUID REFERENCES categorias_financeiras(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT pagamentos_descricao_not_empty CHECK (length(descricao) > 0),
  CONSTRAINT pagamentos_valor_check CHECK (valor > 0)
);
```

### 6. Hiperfocos

```sql
-- Projetos de hiperfoco
CREATE TABLE hiperfoco_projetos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  titulo TEXT NOT NULL,
  descricao TEXT,
  cor TEXT DEFAULT '#3498db',
  tempo_limite INTEGER,
  data_inicio TIMESTAMP WITH TIME ZONE DEFAULT now(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT hiperfoco_projetos_titulo_not_empty CHECK (length(titulo) > 0),
  CONSTRAINT hiperfoco_projetos_tempo_limite_check CHECK (tempo_limite IS NULL OR tempo_limite > 0)
);

-- Tarefas de hiperfoco
CREATE TABLE hiperfoco_tarefas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  projeto_id UUID REFERENCES hiperfoco_projetos(id) ON DELETE CASCADE,
  descricao TEXT NOT NULL,
  concluida BOOLEAN DEFAULT false,
  tarefa_pai_id UUID REFERENCES hiperfoco_tarefas(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT hiperfoco_tarefas_descricao_not_empty CHECK (length(descricao) > 0)
);

-- Sessões de alternância de hiperfoco
CREATE TABLE hiperfoco_sessoes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  projeto_atual_id UUID REFERENCES hiperfoco_projetos(id) ON DELETE SET NULL,
  inicio TIMESTAMP WITH TIME ZONE NOT NULL,
  fim TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

### 7. Prioridades

```sql
-- Prioridades
CREATE TABLE prioridades (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  texto TEXT NOT NULL,
  concluida BOOLEAN DEFAULT false,
  data DATE NOT NULL,
  tipo TEXT DEFAULT 'geral',
  origem_id UUID,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT prioridades_texto_not_empty CHECK (length(texto) > 0),
  CONSTRAINT prioridades_tipo_check CHECK (tipo IN ('geral', 'concurso'))
);
```

### 8. Pomodoro

```sql
-- Configurações do Pomodoro
CREATE TABLE pomodoro_configuracoes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  tempo_foco INTEGER NOT NULL,
  tempo_pausa INTEGER NOT NULL,
  tempo_longa_pausa INTEGER NOT NULL,
  ciclos_antes_longa_pausa INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT pomodoro_configuracoes_user_id_key UNIQUE (user_id),
  CONSTRAINT pomodoro_configuracoes_tempo_foco_check CHECK (tempo_foco > 0),
  CONSTRAINT pomodoro_configuracoes_tempo_pausa_check CHECK (tempo_pausa > 0),
  CONSTRAINT pomodoro_configuracoes_tempo_longa_pausa_check CHECK (tempo_longa_pausa > 0),
  CONSTRAINT pomodoro_configuracoes_ciclos_check CHECK (ciclos_antes_longa_pausa > 0)
);

-- Sessões de Pomodoro
CREATE TABLE pomodoro_sessoes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  inicio TIMESTAMP WITH TIME ZONE NOT NULL,
  fim TIMESTAMP WITH TIME ZONE,
  tipo TEXT NOT NULL,
  ciclo_atual INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT pomodoro_sessoes_tipo_check CHECK (tipo IN ('foco', 'pausa', 'longa_pausa')),
  CONSTRAINT pomodoro_sessoes_ciclo_atual_check CHECK (ciclo_atual > 0)
);
```

### 9. Saúde e Sono

```sql
-- Medicamentos
CREATE TABLE medicamentos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  nome TEXT NOT NULL,
  dosagem TEXT,
  intervalo_horas INTEGER,
  horarios JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT medicamentos_nome_not_empty CHECK (length(nome) > 0),
  CONSTRAINT medicamentos_intervalo_horas_check CHECK (intervalo_horas IS NULL OR intervalo_horas > 0)
);

-- Registros de medicamentos
CREATE TABLE registros_medicamentos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  medicamento_id UUID REFERENCES medicamentos(id) ON DELETE CASCADE,
  data_hora TIMESTAMP WITH TIME ZONE DEFAULT now(),
  tomado BOOLEAN DEFAULT true
);

-- Registros de humor
CREATE TABLE registros_humor (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  nivel INTEGER NOT NULL,
  descricao TEXT,
  fatores TEXT[],
  data_hora TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT registros_humor_nivel_check CHECK (nivel BETWEEN 1 AND 5)
);

-- Registros de sono
CREATE TABLE registros_sono (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  inicio TIMESTAMP WITH TIME ZONE NOT NULL,
  fim TIMESTAMP WITH TIME ZONE,
  qualidade INTEGER,
  observacoes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT registros_sono_qualidade_check CHECK (qualidade IS NULL OR qualidade BETWEEN 1 AND 5)
);

-- Lembretes de sono
CREATE TABLE lembretes_sono (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  tipo TEXT NOT NULL,
  horario TIME NOT NULL,
  dias_semana INTEGER[], -- 0-6 para dias da semana
  ativo BOOLEAN DEFAULT true,
  mensagem TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT lembretes_sono_tipo_check CHECK (tipo IN ('dormir', 'acordar'))
);
```

### 10. Assistente Sati

```sql
-- Conversas com a Sati
CREATE TABLE sati_conversas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  titulo TEXT,
  origem TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT sati_conversas_origem_check CHECK (origem IN ('whatsapp', 'web'))
);

-- Mensagens das conversas
CREATE TABLE sati_mensagens (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversa_id UUID REFERENCES sati_conversas(id) ON DELETE CASCADE,
  remetente TEXT NOT NULL,
  conteudo TEXT NOT NULL,
  tipo_conteudo TEXT DEFAULT 'texto',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT sati_mensagens_remetente_check CHECK (remetente IN ('usuario', 'sati')),
  CONSTRAINT sati_mensagens_tipo_conteudo_check CHECK (tipo_conteudo IN ('texto', 'imagem', 'audio'))
);

-- Configurações da Sati por usuário
CREATE TABLE sati_configuracoes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  whatsapp_ativo BOOLEAN DEFAULT false,
  numero_whatsapp TEXT,
  notificacoes_ativas BOOLEAN DEFAULT true,
  tom_voz TEXT DEFAULT 'amigavel',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(user_id)
);
```

## Políticas de Segurança (RLS)

Para garantir a segurança dos dados, todas as tabelas devem implementar políticas de Row Level Security (RLS) no Supabase. Abaixo está um modelo básico de política que deve ser aplicado a todas as tabelas:

```sql
-- Habilitar RLS na tabela
ALTER TABLE [TABELA] ENABLE ROW LEVEL SECURITY;

-- Política para leitura (usuário só pode ver seus próprios dados)
CREATE POLICY "Usuários podem ler apenas seus próprios dados" ON [TABELA]
  FOR SELECT
  USING (auth.uid() = user_id);

-- Política para inserção (usuário só pode inserir seus próprios dados)
CREATE POLICY "Usuários podem inserir apenas seus próprios dados" ON [TABELA]
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Política para atualização (usuário só pode atualizar seus próprios dados)
CREATE POLICY "Usuários podem atualizar apenas seus próprios dados" ON [TABELA]
  FOR UPDATE
  USING (auth.uid() = user_id);

-- Política para exclusão (usuário só pode excluir seus próprios dados)
CREATE POLICY "Usuários podem excluir apenas seus próprios dados" ON [TABELA]
  FOR DELETE
  USING (auth.uid() = user_id);
```

Para tabelas com relacionamentos, como `conteudo_programatico` que não tem `user_id` diretamente, a política deve verificar o `user_id` da tabela pai:

```sql
CREATE POLICY "Usuários podem ler apenas seu próprio conteúdo programático" ON conteudo_programatico
  FOR SELECT
  USING (auth.uid() IN (
    SELECT user_id FROM concursos WHERE id = conteudo_programatico.concurso_id
  ));
```

## Índices para Otimização

Para otimizar o desempenho do banco de dados, os seguintes índices devem ser criados:

```sql
-- Índices para busca textual
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX receitas_nome_idx ON receitas USING GIN (nome gin_trgm_ops);
CREATE INDEX notas_autoconhecimento_titulo_idx ON notas_autoconhecimento USING GIN (titulo gin_trgm_ops);
CREATE INDEX notas_autoconhecimento_conteudo_idx ON notas_autoconhecimento USING GIN (conteudo gin_trgm_ops);

-- Índices para consultas frequentes
CREATE INDEX registros_sono_user_id_inicio_idx ON registros_sono(user_id, inicio);
CREATE INDEX gastos_user_id_data_idx ON transacoes(user_id, data);
CREATE INDEX refeicoes_user_id_data_idx ON refeicoes(user_id, data);
CREATE INDEX concursos_user_id_status_idx ON concursos(user_id, status);
CREATE INDEX concursos_user_id_data_prova_idx ON concursos(user_id, data_prova);
CREATE INDEX prioridades_user_id_data_idx ON prioridades(user_id, data);
CREATE INDEX prioridades_user_id_concluida_idx ON prioridades(user_id, concluida);
CREATE INDEX prioridades_user_id_tipo_origem_id_idx ON prioridades(user_id, tipo, origem_id);
CREATE INDEX hiperfoco_projetos_user_id_data_inicio_idx ON hiperfoco_projetos(user_id, data_inicio);
CREATE INDEX sessoes_estudo_user_id_inicio_idx ON sessoes_estudo(user_id, inicio);
CREATE INDEX sessoes_estudo_user_id_completo_idx ON sessoes_estudo(user_id, completo);
```

## Conclusão

Este modelo lógico do banco de dados foi projetado para atender às necessidades do projeto StayFocus, com base na análise da estrutura atual das stores. O modelo inclui todas as entidades identificadas, seus relacionamentos, constraints e validações necessárias para garantir a integridade dos dados.

As principais características do modelo são:

1. **Organização por domínios funcionais**: As tabelas estão agrupadas por domínios como Usuários, Alimentação, Estudos, Finanças, etc.
2. **Chaves primárias e estrangeiras**: Todas as tabelas possuem chaves primárias UUID e as relações entre tabelas são estabelecidas por chaves estrangeiras.
3. **Constraints e validações**: Foram adicionadas constraints para garantir a integridade dos dados, como verificações de valores não vazios, intervalos válidos, etc.
4. **Políticas de segurança**: O modelo inclui políticas de Row Level Security para garantir que os usuários só possam acessar seus próprios dados.
5. **Índices para otimização**: Foram definidos índices para melhorar o desempenho das consultas mais frequentes.

Este modelo servirá como base para a implementação das migrações iniciais no Supabase, conforme previsto na próxima etapa da Sprint 1.