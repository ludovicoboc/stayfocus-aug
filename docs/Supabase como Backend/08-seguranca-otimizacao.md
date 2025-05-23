# Segurança e Otimização

## Contexto

A segurança e a otimização são aspectos críticos para garantir que o StayFocus seja uma aplicação confiável, eficiente e escalável. O Supabase oferece diversas ferramentas e recursos para implementar medidas de segurança robustas e otimizar o desempenho do banco de dados.

Neste documento, abordaremos as principais práticas de segurança e otimização a serem implementadas no projeto StayFocus, incluindo políticas de Row Level Security (RLS), índices para otimização de consultas, backups automáticos e monitoramento de desempenho.

## Implementação de Políticas de Segurança (RLS)

O Row Level Security (RLS) é um recurso poderoso do PostgreSQL que permite controlar o acesso aos dados em nível de linha, garantindo que os usuários só possam acessar os dados que lhes pertencem.

### 1. Políticas RLS para Todas as Tabelas

Todas as tabelas do StayFocus devem ter políticas RLS habilitadas:

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
ALTER TABLE hiperfoco_projetos ENABLE ROW LEVEL SECURITY;
ALTER TABLE hiperfoco_tarefas ENABLE ROW LEVEL SECURITY;
ALTER TABLE pomodoro_sessoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE registros_sono ENABLE ROW LEVEL SECURITY;
ALTER TABLE medicamentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE registros_medicamentos ENABLE ROW LEVEL SECURITY;
```

### 2. Políticas de Acesso Padrão

Para cada tabela, devemos implementar políticas para as operações CRUD (Create, Read, Update, Delete):

```sql
-- Exemplo para a tabela hiperfoco_projetos

-- Política para leitura (SELECT)
CREATE POLICY "Usuários podem ler apenas seus próprios hiperfocos"
ON hiperfoco_projetos FOR SELECT
USING (auth.uid() = user_id);

-- Política para inserção (INSERT)
CREATE POLICY "Usuários podem inserir apenas seus próprios hiperfocos"
ON hiperfoco_projetos FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Política para atualização (UPDATE)
CREATE POLICY "Usuários podem atualizar apenas seus próprios hiperfocos"
ON hiperfoco_projetos FOR UPDATE
USING (auth.uid() = user_id);

-- Política para exclusão (DELETE)
CREATE POLICY "Usuários podem excluir apenas seus próprios hiperfocos"
ON hiperfoco_projetos FOR DELETE
USING (auth.uid() = user_id);
```

### 3. Políticas para Tabelas com Relacionamentos

Para tabelas que têm relacionamentos, como `hiperfoco_tarefas` (que se relaciona com `hiperfoco_projetos`), precisamos de políticas mais complexas:

```sql
-- Política para leitura de tarefas de hiperfoco
CREATE POLICY "Usuários podem ler tarefas de seus próprios hiperfocos"
ON hiperfoco_tarefas FOR SELECT
USING (
  EXISTS (
    SELECT 1
    FROM hiperfoco_projetos
    WHERE hiperfoco_projetos.id = hiperfoco_tarefas.projeto_id
    AND hiperfoco_projetos.user_id = auth.uid()
  )
);

-- Política para inserção de tarefas de hiperfoco
CREATE POLICY "Usuários podem inserir tarefas em seus próprios hiperfocos"
ON hiperfoco_tarefas FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1
    FROM hiperfoco_projetos
    WHERE hiperfoco_projetos.id = hiperfoco_tarefas.projeto_id
    AND hiperfoco_projetos.user_id = auth.uid()
  )
);

-- Políticas semelhantes para UPDATE e DELETE
```

### 4. Políticas para Acesso Administrativo

Para permitir que administradores acessem dados para suporte ao usuário:

```sql
-- Criar role para administradores
CREATE ROLE app_admin;

-- Conceder permissões à role
GRANT USAGE ON SCHEMA public TO app_admin;
GRANT ALL ON ALL TABLES IN SCHEMA public TO app_admin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO app_admin;

-- Política para acesso administrativo
CREATE POLICY "Administradores podem acessar todos os dados"
ON hiperfoco_projetos
USING (
  auth.jwt() -> 'app_metadata' ->> 'role' = 'admin'
);
```

## Otimização de Consultas

### 1. Índices para Campos Frequentemente Consultados

```sql
-- Índices para chaves estrangeiras
CREATE INDEX hiperfoco_tarefas_projeto_id_idx ON hiperfoco_tarefas(projeto_id);
CREATE INDEX conteudo_programatico_concurso_id_idx ON conteudo_programatico(concurso_id);
CREATE INDEX registros_medicamentos_medicamento_id_idx ON registros_medicamentos(medicamento_id);

-- Índices para campos de data/hora
CREATE INDEX refeicoes_data_idx ON refeicoes(data);
CREATE INDEX hidratacao_data_idx ON hidratacao(data);
CREATE INDEX registros_sono_inicio_idx ON registros_sono(inicio);
CREATE INDEX pomodoro_sessoes_inicio_idx ON pomodoro_sessoes(inicio);

-- Índices para campos de status
CREATE INDEX concursos_status_idx ON concursos(status);
```

### 2. Índices para Busca Textual

```sql
-- Extensão para busca textual
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Índices para busca textual
CREATE INDEX receitas_nome_idx ON receitas USING GIN (nome gin_trgm_ops);
CREATE INDEX notas_autoconhecimento_titulo_idx ON notas_autoconhecimento USING GIN (titulo gin_trgm_ops);
CREATE INDEX notas_autoconhecimento_conteudo_idx ON notas_autoconhecimento USING GIN (conteudo gin_trgm_ops);
CREATE INDEX concursos_titulo_idx ON concursos USING GIN (titulo gin_trgm_ops);
```

### 3. Índices Compostos para Consultas Específicas

```sql
-- Índice composto para consultas de refeições por usuário e data
CREATE INDEX refeicoes_user_id_data_idx ON refeicoes(user_id, data);

-- Índice composto para consultas de hidratação por usuário e data
CREATE INDEX hidratacao_user_id_data_idx ON hidratacao(user_id, data);

-- Índice composto para consultas de sono por usuário e período
CREATE INDEX registros_sono_user_id_inicio_idx ON registros_sono(user_id, inicio);
```

### 4. Otimização de Consultas Frequentes

Para consultas frequentes, podemos criar views materializadas:

```sql
-- View materializada para estatísticas de sono
CREATE MATERIALIZED VIEW estatisticas_sono AS
SELECT
  user_id,
  date_trunc('month', inicio) AS mes,
  AVG(EXTRACT(EPOCH FROM (fim - inicio)) / 3600) AS media_horas_sono,
  AVG(qualidade) AS media_qualidade
FROM registros_sono
WHERE fim IS NOT NULL
GROUP BY user_id, date_trunc('month', inicio);

-- Índice para a view materializada
CREATE INDEX estatisticas_sono_user_id_mes_idx ON estatisticas_sono(user_id, mes);

-- Função para atualizar a view materializada
CREATE OR REPLACE FUNCTION refresh_estatisticas_sono()
RETURNS TRIGGER AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY estatisticas_sono;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar a view materializada
CREATE TRIGGER refresh_estatisticas_sono_trigger
AFTER INSERT OR UPDATE OR DELETE ON registros_sono
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_estatisticas_sono();
```

## Configuração de Backups Automáticos

### 1. Backups Diários

O Supabase oferece backups automáticos diários por padrão. Para garantir a segurança dos dados, é importante verificar se os backups estão configurados corretamente:

1. Acesse o painel do Supabase e navegue até "Settings" > "Database"
2. Na seção "Backups", verifique se os backups diários estão habilitados
3. Configure a retenção de backups para pelo menos 7 dias

### 2. Point-in-Time Recovery (PITR)

Para maior segurança, habilite o Point-in-Time Recovery, que permite restaurar o banco de dados para qualquer momento dentro do período de retenção:

1. Acesse o painel do Supabase e navegue até "Settings" > "Database"
2. Na seção "PITR", habilite o Point-in-Time Recovery
3. Configure o período de retenção para 7 dias (ou mais, dependendo das necessidades)

### 3. Exportações Manuais

Além dos backups automáticos, é recomendável realizar exportações manuais periódicas:

```sql
-- Criar função para exportar dados de um usuário
CREATE OR REPLACE FUNCTION export_user_data(user_uuid UUID)
RETURNS JSON AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'user_profile', (SELECT row_to_json(u) FROM user_profiles u WHERE u.id = user_uuid),
    'user_preferences', (SELECT row_to_json(p) FROM user_preferences p WHERE p.user_id = user_uuid),
    'hiperfocos', (
      SELECT json_agg(h)
      FROM (
        SELECT h.*, (
          SELECT json_agg(t)
          FROM hiperfoco_tarefas t
          WHERE t.projeto_id = h.id
        ) AS tarefas
        FROM hiperfoco_projetos h
        WHERE h.user_id = user_uuid
      ) h
    ),
    'concursos', (
      SELECT json_agg(c)
      FROM (
        SELECT c.*, (
          SELECT json_agg(cp)
          FROM conteudo_programatico cp
          WHERE cp.concurso_id = c.id
        ) AS conteudo
        FROM concursos c
        WHERE c.user_id = user_uuid
      ) c
    ),
    'refeicoes', (SELECT json_agg(r) FROM refeicoes r WHERE r.user_id = user_uuid),
    'hidratacao', (SELECT json_agg(h) FROM hidratacao h WHERE h.user_id = user_uuid),
    'notas_autoconhecimento', (SELECT json_agg(n) FROM notas_autoconhecimento n WHERE n.user_id = user_uuid),
    'registros_sono', (SELECT json_agg(s) FROM registros_sono s WHERE s.user_id = user_uuid),
    'medicamentos', (
      SELECT json_agg(m)
      FROM (
        SELECT m.*, (
          SELECT json_agg(r)
          FROM registros_medicamentos r
          WHERE r.medicamento_id = m.id
        ) AS registros
        FROM medicamentos m
        WHERE m.user_id = user_uuid
      ) m
    )
  ) INTO result;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Restringir acesso à função
REVOKE ALL ON FUNCTION export_user_data(UUID) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION export_user_data(UUID) TO authenticated;
```

## Monitoramento e Otimização Contínua

### 1. Monitoramento de Desempenho

Para monitorar o desempenho do banco de dados, utilize as ferramentas do PostgreSQL:

```sql
-- Visualizar consultas lentas
SELECT
  query,
  calls,
  total_time,
  mean_time,
  rows
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Visualizar uso de índices
SELECT
  schemaname,
  relname,
  indexrelname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC
LIMIT 10;
```

### 2. Otimização de Tabelas

Realize manutenção periódica das tabelas para garantir desempenho ótimo:

```sql
-- Analisar tabelas para atualizar estatísticas
ANALYZE;

-- Vacuum para recuperar espaço
VACUUM FULL;

-- Reindexar para otimizar índices
REINDEX DATABASE postgres;
```

### 3. Configuração de Alertas

Configure alertas para monitorar o desempenho e a segurança do banco de dados:

1. Acesse o painel do Supabase e navegue até "Settings" > "Database"
2. Configure alertas para:
   - Uso de CPU acima de 80%
   - Uso de memória acima de 80%
   - Espaço em disco abaixo de 20%
   - Falhas de conexão acima do normal
   - Consultas lentas (acima de 1 segundo)

## Práticas de Segurança Adicionais

### 1. Validação de Entrada

Implemente validação rigorosa de entrada no frontend e no backend:

```typescript
// Exemplo de validação com Zod no frontend
import { z } from 'zod'

const HiperfocoSchema = z.object({
  titulo: z.string().min(1, 'O título é obrigatório').max(100, 'O título deve ter no máximo 100 caracteres'),
  descricao: z.string().max(500, 'A descrição deve ter no máximo 500 caracteres'),
  cor: z.string().regex(/^#[0-9A-F]{6}$/i, 'Cor inválida'),
  tempoLimite: z.number().optional()
})

// Validar dados antes de enviar para o Supabase
const validarHiperfoco = (dados: unknown) => {
  return HiperfocoSchema.parse(dados)
}
```

### 2. Proteção contra SQL Injection

O Supabase já oferece proteção contra SQL Injection através de consultas parametrizadas, mas é importante garantir que todas as consultas sigam esse padrão:

```typescript
// Correto: Usar métodos do cliente Supabase
const { data } = await supabase
  .from('hiperfoco_projetos')
  .select('*')
  .eq('user_id', userId)

// Incorreto: Concatenar strings em consultas SQL
const { data } = await supabase.rpc('consulta_personalizada', {
  sql_query: `SELECT * FROM hiperfoco_projetos WHERE user_id = '${userId}'` // Vulnerável a SQL Injection
})
```

### 3. Auditoria de Acesso

Implemente um sistema de auditoria para registrar ações importantes:

```sql
-- Criar tabela de auditoria
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  action TEXT NOT NULL,
  table_name TEXT NOT NULL,
  record_id UUID,
  old_data JSONB,
  new_data JSONB,
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Função para registrar ações
CREATE OR REPLACE FUNCTION log_action()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_logs (
    user_id,
    action,
    table_name,
    record_id,
    old_data,
    new_data
  )
  VALUES (
    auth.uid(),
    TG_OP,
    TG_TABLE_NAME,
    CASE
      WHEN TG_OP = 'DELETE' THEN OLD.id
      ELSE NEW.id
    END,
    CASE
      WHEN TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN to_jsonb(OLD)
      ELSE NULL
    END,
    CASE
      WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN to_jsonb(NEW)
      ELSE NULL
    END
  );
  
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Aplicar trigger a tabelas importantes
CREATE TRIGGER log_hiperfoco_projetos
AFTER INSERT OR UPDATE OR DELETE ON hiperfoco_projetos
FOR EACH ROW EXECUTE FUNCTION log_action();
```

## Próximos Passos

Após implementar as medidas de segurança e otimização, os próximos passos são:

1. Realizar testes de carga para verificar o desempenho sob diferentes condições
2. Implementar monitoramento contínuo para identificar e resolver problemas rapidamente
3. Revisar e atualizar regularmente as políticas de segurança
4. Documentar todas as medidas de segurança e otimização implementadas

A segurança e a otimização são processos contínuos que requerem atenção constante para garantir que o StayFocus seja uma aplicação confiável, eficiente e escalável.
