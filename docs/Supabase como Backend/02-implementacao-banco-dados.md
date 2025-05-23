# Implementação do Esquema de Banco de Dados

## Contexto

A implementação do esquema de banco de dados é uma etapa fundamental na migração do StayFocus para o Supabase. O modelo lógico do banco de dados foi cuidadosamente projetado com base na análise da estrutura atual das stores Zustand e nos requisitos especificados na documentação do projeto.

O Supabase utiliza PostgreSQL como banco de dados, o que permite aproveitar recursos avançados como tipos de dados JSON, arrays, funções e triggers, além de políticas de segurança em nível de linha (Row Level Security - RLS).

## Tabelas Principais

Com base na documentação existente, as seguintes tabelas principais devem ser implementadas:

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
```

### 2. Alimentação e Hidratação

```sql
-- Refeições
CREATE TABLE refeicoes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  data TIMESTAMP WITH TIME ZONE NOT NULL,
  tipo TEXT NOT NULL,
  descricao TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Hidratação
CREATE TABLE hidratacao (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  data TIMESTAMP WITH TIME ZONE NOT NULL,
  quantidade_ml INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
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

### 4. Concursos e Estudos

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
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

## Implementação de Funções e Triggers

Para garantir a integridade dos dados e automatizar certas operações, é necessário implementar funções e triggers no PostgreSQL:

### 1. Função para Atualização de Timestamp

```sql
-- Função para atualizar o campo updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 2. Triggers para Atualização Automática

```sql
-- Trigger para user_profiles
CREATE TRIGGER set_updated_at_user_profiles
BEFORE UPDATE ON user_profiles
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger para user_preferences
CREATE TRIGGER set_updated_at_user_preferences
BEFORE UPDATE ON user_preferences
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger para receitas
CREATE TRIGGER set_updated_at_receitas
BEFORE UPDATE ON receitas
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger para notas_autoconhecimento
CREATE TRIGGER set_updated_at_notas_autoconhecimento
BEFORE UPDATE ON notas_autoconhecimento
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger para concursos
CREATE TRIGGER set_updated_at_concursos
BEFORE UPDATE ON concursos
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger para conteudo_programatico
CREATE TRIGGER set_updated_at_conteudo_programatico
BEFORE UPDATE ON conteudo_programatico
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

## Políticas de Row Level Security (RLS)

Para garantir a segurança dos dados, todas as tabelas devem implementar políticas de Row Level Security (RLS) no Supabase:

```sql
-- Habilitar RLS em todas as tabelas
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE refeicoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE hidratacao ENABLE ROW LEVEL SECURITY;
ALTER TABLE receitas ENABLE ROW LEVEL SECURITY;
ALTER TABLE notas_autoconhecimento ENABLE ROW LEVEL SECURITY;
ALTER TABLE concursos ENABLE ROW LEVEL SECURITY;
ALTER TABLE conteudo_programatico ENABLE ROW LEVEL SECURITY;

-- Política para leitura (usuário só pode ver seus próprios dados)
CREATE POLICY "Usuários podem ler apenas seus próprios dados" ON user_profiles
  FOR SELECT
  USING (auth.uid() = id);

-- Política para inserção (usuário só pode inserir seus próprios dados)
CREATE POLICY "Usuários podem inserir apenas seus próprios dados" ON user_profiles
  FOR INSERT
  WITH CHECK (auth.uid() = id);

-- Política para atualização (usuário só pode atualizar seus próprios dados)
CREATE POLICY "Usuários podem atualizar apenas seus próprios dados" ON user_profiles
  FOR UPDATE
  USING (auth.uid() = id);

-- Política para exclusão (usuário só pode excluir seus próprios dados)
CREATE POLICY "Usuários podem excluir apenas seus próprios dados" ON user_profiles
  FOR DELETE
  USING (auth.uid() = id);
```

Políticas semelhantes devem ser aplicadas a todas as outras tabelas, substituindo `user_profiles` pelo nome da tabela e ajustando a condição `auth.uid() = id` para `auth.uid() = user_id` quando apropriado.

## Índices para Otimização

Para otimizar o desempenho do banco de dados, os seguintes índices devem ser criados:

```sql
-- Extensão para busca textual
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Índices para busca textual
CREATE INDEX receitas_nome_idx ON receitas USING GIN (nome gin_trgm_ops);
CREATE INDEX notas_autoconhecimento_titulo_idx ON notas_autoconhecimento USING GIN (titulo gin_trgm_ops);
CREATE INDEX notas_autoconhecimento_conteudo_idx ON notas_autoconhecimento USING GIN (conteudo gin_trgm_ops);
CREATE INDEX concursos_titulo_idx ON concursos USING GIN (titulo gin_trgm_ops);

-- Índices para chaves estrangeiras
CREATE INDEX refeicoes_user_id_idx ON refeicoes(user_id);
CREATE INDEX hidratacao_user_id_idx ON hidratacao(user_id);
CREATE INDEX receitas_user_id_idx ON receitas(user_id);
CREATE INDEX notas_autoconhecimento_user_id_idx ON notas_autoconhecimento(user_id);
CREATE INDEX concursos_user_id_idx ON concursos(user_id);
CREATE INDEX conteudo_programatico_concurso_id_idx ON conteudo_programatico(concurso_id);

-- Índices para consultas frequentes
CREATE INDEX refeicoes_data_idx ON refeicoes(data);
CREATE INDEX hidratacao_data_idx ON hidratacao(data);
CREATE INDEX concursos_status_idx ON concursos(status);
```

## Implementação Prática

Para implementar o esquema de banco de dados no Supabase, você pode:

1. **Usar o Editor SQL no MCP**: Acesse o painel do Supabase, vá para "SQL Editor" e execute os scripts SQL para criar as tabelas, funções, triggers, políticas e índices.

2. **Usar Migrações com Supabase CLI**: Para ambientes de desenvolvimento e produção, é recomendável usar o Supabase CLI para gerenciar migrações de banco de dados.

```bash
# Instalar Supabase CLI
npm install -g supabase

# Inicializar projeto Supabase local
supabase init

# Criar uma nova migração
supabase migration new create_initial_schema

# Aplicar migrações
supabase db push
```

3. **Integrar com o Backend FastAPI**: Utilize o cliente Supabase configurado anteriormente para interagir com o banco de dados a partir do backend FastAPI.

## Próximos Passos

Após a implementação do esquema de banco de dados, os próximos passos são:

1. Configurar o sistema de autenticação
2. Implementar a integração com o frontend
3. Configurar o armazenamento de arquivos (Storage)
4. Desenvolver as Edge Functions necessárias

A implementação correta do esquema de banco de dados é fundamental para garantir a integridade, segurança e desempenho dos dados no StayFocus.
