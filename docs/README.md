# Documentação do StayFocus

Bem-vindo à documentação completa do projeto StayFocus - uma aplicação abrangente para gerenciamento de produtividade, foco e bem-estar.

## 📋 Índice

### 📖 Documentação Principal
- [Contexto e Visão Geral](./01-overview/context.md) - Objetivos, missão e diferencial competitivo
- [Especificações Técnicas](./02-technical/especificacoes.md) - Detalhes técnicos de migração para Supabase
- [Estrutura do Banco de Dados](./02-technical/estrutura_banco_dados.md) - Schema e modelagem de dados

### 🏗️ Arquitetura e Implementação
- [Plano de Implementação](./03-implementation/plano_implementacao.md) - Visão geral do roadmap
- [Plano de Reestruturação](./03-implementation/plano_reestruturacao.md) - Organização do código
- [Integração Azure](./02-technical/azure_integration.md) - Possibilidades da Azure CLI

### 🚀 Sprints de Desenvolvimento

#### Fase 1: Infraestrutura (Sprints 1-3)
- [Sprint 1-3: Infraestrutura e Migração](./04-sprints/fase-1-infraestrutura/sprint_1-3_infraestrutura.md)

#### Fase 2: Assistente Virtual (Sprints 4-7)
- [Sprint 4-7: Desenvolvimento da Sati](./04-sprints/fase-2-sati/sprint_4-7_sati.md)

#### Fase 3: Mobile e Funcionalidades Avançadas (Sprints 8-12)
- [Sprint 8-12: Desenvolvimento Mobile](./04-sprints/fase-3-mobile/sprint_8-12_avancado_mobile.md)

#### Fase 4: Testes e Lançamento (Sprints 13-15)
- [Sprint 13-15: Testes e Lançamento](./04-sprints/fase-4-lancamento/sprint_13-15_testes_lancamento.md)

## 🎯 Sobre o Projeto

O **StayFocus** é uma aplicação inovadora projetada para auxiliar estudantes, profissionais e pessoas com TDAH a gerenciar sua produtividade de forma holística, integrando aspectos como alimentação, sono, lazer e bem-estar geral.

### Principais Funcionalidades
- ⏰ Gerenciamento de tempo com técnica Pomodoro
- 📚 Ferramentas para estudo e preparação para concursos
- 🍎 Monitoramento de alimentação e hidratação
- 😴 Acompanhamento de padrões de sono
- 🤖 Assistente virtual (Sati) com IA
- 📱 Aplicação mobile multiplataforma
- 🔄 Sincronização em tempo real entre dispositivos

### Tecnologias
- **Frontend**: Next.js, React, Zustand, Tailwind CSS
- **Backend**: Supabase (PostgreSQL, Auth, Storage, Functions)
- **IA**: Maritaca AI (Modelo Sabiá 3) com sistema RAG
- **Mobile**: React Native / Expo
- **Integração**: WhatsApp API

## 📁 Estrutura da Documentação

```
docs/
├── README.md                           # Este arquivo
├── 01-overview/                        # Visão geral do projeto
│   └── context.md
├── 02-technical/                       # Documentação técnica
│   ├── especificacoes.md
│   ├── estrutura_banco_dados.md
│   └── azure_integration.md
├── 03-implementation/                  # Planejamento e implementação
│   ├── plano_implementacao.md
│   └── plano_reestruturacao.md
└── 04-sprints/                         # Sprints organizadas por fase
    ├── fase-1-infraestrutura/
    ├── fase-2-sati/
    ├── fase-3-mobile/
    └── fase-4-lancamento/
```

## 🚀 Como Começar

1. Leia o [contexto geral](./01-overview/context.md) para entender os objetivos do projeto
2. Consulte as [especificações técnicas](./02-technical/especificacoes.md) para detalhes de implementação
3. Siga o [plano de implementação](./03-implementation/plano_implementacao.md) para o roadmap de desenvolvimento
4. Execute as sprints conforme documentado na pasta [04-sprints](./04-sprints/)

## 📝 Contribuindo

Para contribuir com a documentação:
1. Mantenha a estrutura organizacional
2. Documente mudanças significativas
3. Atualize o README principal quando necessário
4. Use markdown padrão para formatação

## 📞 Contato

Para dúvidas sobre a documentação ou o projeto, consulte os arquivos específicos ou entre em contato com a equipe de desenvolvimento.
