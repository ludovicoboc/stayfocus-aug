h# Análise de Contexto e Padrões - SATI

## Objetivo
Implementar um sistema avançado de análise de contexto que permita ao SATI entender os padrões de produtividade do usuário e fornecer insights personalizados.

## Componentes da Análise

### 1. Context Manager
```typescript
// src/services/contextManager.ts
import { supabase } from './supabaseClient';

export interface UserPattern {
  type: 'productivity' | 'schedule' | 'behavior' | 'preference';
  pattern: string;
  confidence: number;
  evidence: any[];
  lastObserved: Date;
  trend: 'improving' | 'declining' | 'stable';
}

export interface ProductivityMetrics {
  dailyAverage: number;
  weeklyTrend: number;
  peakHours: number[];
  lowEnergyPeriods: number[];
  completionRate: number;
  averageSessionDuration: number;
  interruptionFrequency: number;
  focusQuality: number;
}

export interface ContextualInsights {
  currentState: 'focused' | 'distracted' | 'tired' | 'energetic' | 'neutral';
  optimalNextAction: string;
  riskFactors: string[];
  opportunities: string[];
  recommendations: string[];
}

export class ContextManager {
  async buildContext(userId: string): Promise<SATIContext> {
    try {
      const [
        currentTask,
        recentSessions,
        userSettings,
        productivityMetrics
      ] = await Promise.all([
        this.getCurrentTask(userId),
        this.getRecentSessions(userId),
        this.getUserSettings(userId),
        this.getProductivityMetrics(userId)
      ]);

      const timeContext = this.getTimeContext();
      
      return {
        currentTask,
        recentSessions,
        userSettings,
        productivityMetrics,
        ...timeContext
      };
    } catch (error) {
      console.error('Erro ao construir contexto:', error);
      throw error;
    }
  }

  async analyzeUserPatterns(userId: string): Promise<UserPattern[]> {
    try {
      const patterns: UserPattern[] = [];

      // Analisar padrões de produtividade
      const productivityPatterns = await this.analyzeProductivityPatterns(userId);
      patterns.push(...productivityPatterns);

      // Analisar padrões de horário
      const schedulePatterns = await this.analyzeSchedulePatterns(userId);
      patterns.push(...schedulePatterns);

      // Analisar padrões comportamentais
      const behaviorPatterns = await this.analyzeBehaviorPatterns(userId);
      patterns.push(...behaviorPatterns);

      // Analisar preferências
      const preferencePatterns = await this.analyzePreferencePatterns(userId);
      patterns.push(...preferencePatterns);

      return patterns.filter(p => p.confidence > 0.6);
    } catch (error) {
      console.error('Erro na análise de padrões:', error);
      return [];
    }
  }

  async generateContextualInsights(userId: string, context: SATIContext): Promise<ContextualInsights> {
    try {
      const patterns = await this.analyzeUserPatterns(userId);
      const currentState = this.assessCurrentState(context, patterns);
      
      return {
        currentState,
        optimalNextAction: this.suggestOptimalAction(currentState, context, patterns),
        riskFactors: this.identifyRiskFactors(context, patterns),
        opportunities: this.identifyOpportunities(context, patterns),
        recommendations: this.generateRecommendations(currentState, context, patterns)
      };
    } catch (error) {
      console.error('Erro ao gerar insights contextuais:', error);
      throw error;
    }
  }

  private async analyzeProductivityPatterns(userId: string): Promise<UserPattern[]> {
    const patterns: UserPattern[] = [];

    // Buscar dados dos últimos 30 dias
    const { data: sessions } = await supabase
      .from('pomodoro_sessions')
      .select('*')
      .eq('user_id', userId)
      .gte('started_at', new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString())
      .eq('completed', true);

    if (!sessions || sessions.length < 10) {
      return patterns; // Dados insuficientes
    }

    // Padrão 1: Horários de maior produtividade
    const hourlyProductivity = this.calculateHourlyProductivity(sessions);
    const peakHours = Object.entries(hourlyProductivity)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3)
      .map(([hour]) => parseInt(hour));

    if (peakHours.length > 0) {
      patterns.push({
        type: 'productivity',
        pattern: `peak_hours_${peakHours.join('_')}`,
        confidence: this.calculateConfidence(hourlyProductivity, peakHours),
        evidence: sessions.filter(s => peakHours.includes(new Date(s.started_at).getHours())),
        lastObserved: new Date(),
        trend: this.calculateTrend(sessions, 'productivity')
      });
    }

    // Padrão 2: Duração ótima de sessões
    const avgDuration = sessions.reduce((acc, s) => acc + s.duration, 0) / sessions.length;
    const optimalDuration = this.findOptimalSessionDuration(sessions);

    if (Math.abs(avgDuration - optimalDuration) > 300) { // 5 minutos de diferença
      patterns.push({
        type: 'productivity',
        pattern: `optimal_duration_${Math.round(optimalDuration / 60)}min`,
        confidence: 0.8,
        evidence: sessions,
        lastObserved: new Date(),
        trend: 'stable'
      });
    }

    // Padrão 3: Frequência de interrupções
    const avgInterruptions = sessions.reduce((acc, s) => acc + (s.interruptions || 0), 0) / sessions.length;
    
    if (avgInterruptions > 2) {
      patterns.push({
        type: 'productivity',
        pattern: 'high_interruption_frequency',
        confidence: 0.9,
        evidence: sessions.filter(s => (s.interruptions || 0) > 2),
        lastObserved: new Date(),
        trend: this.calculateInterruptionTrend(sessions)
      });
    }

    return patterns;
  }

  private async analyzeSchedulePatterns(userId: string): Promise<UserPattern[]> {
    const patterns: UserPattern[] = [];

    const { data: sessions } = await supabase
      .from('pomodoro_sessions')
      .select('started_at, completed')
      .eq('user_id', userId)
      .gte('started_at', new Date(Date.now() - 21 * 24 * 60 * 60 * 1000).toISOString());

    if (!sessions || sessions.length < 20) return patterns;

    // Padrão de dias da semana
    const weekdayActivity = this.analyzeWeekdayActivity(sessions);
    const mostActiveDay = Object.entries(weekdayActivity).reduce((a, b) => weekdayActivity[a[0]] > weekdayActivity[b[0]] ? a : b)[0];

    patterns.push({
      type: 'schedule',
      pattern: `most_active_${mostActiveDay}`,
      confidence: 0.85,
      evidence: sessions.filter(s => new Date(s.started_at).getDay().toString() === mostActiveDay),
      lastObserved: new Date(),
      trend: 'stable'
    });

    // Padrão de consistência
    const dailyConsistency = this.calculateDailyConsistency(sessions);
    
    if (dailyConsistency > 0.7) {
      patterns.push({
        type: 'schedule',
        pattern: 'high_consistency',
        confidence: dailyConsistency,
        evidence: sessions,
        lastObserved: new Date(),
        trend: 'stable'
      });
    }

    return patterns;
  }

  private async analyzeBehaviorPatterns(userId: string): Promise<UserPattern[]> {
    const patterns: UserPattern[] = [];

    // Analisar interações com SATI
    const { data: interactions } = await supabase
      .from('sati_interactions')
      .select('*')
      .eq('user_id', userId)
      .gte('created_at', new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString());

    if (interactions && interactions.length > 5) {
      // Padrão de tipos de pergunta
      const questionTypes = this.categorizeQuestions(interactions);
      const dominantType = Object.entries(questionTypes).reduce((a, b) => a[1] > b[1] ? a : b)[0];

      patterns.push({
        type: 'behavior',
        pattern: `frequent_${dominantType}_questions`,
        confidence: 0.8,
        evidence: interactions.filter(i => this.categorizeQuestion(i.user_message) === dominantType),
        lastObserved: new Date(),
        trend: 'stable'
      });

      // Padrão de horários de interação
      const interactionHours = interactions.map(i => new Date(i.created_at).getHours());
      const commonHour = this.findMostCommonHour(interactionHours);

      patterns.push({
        type: 'behavior',
        pattern: `sati_usage_hour_${commonHour}`,
        confidence: 0.75,
        evidence: interactions.filter(i => new Date(i.created_at).getHours() === commonHour),
        lastObserved: new Date(),
        trend: 'stable'
      });
    }

    return patterns;
  }

  private async analyzePreferencePatterns(userId: string): Promise<UserPattern[]> {
    const patterns: UserPattern[] = [];

    const { data: settings } = await supabase
      .from('user_settings')
      .select('*')
      .eq('user_id', userId)
      .single();

    if (!settings) return patterns;

    // Preferências de duração
    if (settings.focus_duration !== 1500) { // Não é o padrão de 25 min
      patterns.push({
        type: 'preference',
        pattern: `custom_focus_duration_${settings.focus_duration}`,
        confidence: 1.0,
        evidence: [settings],
        lastObserved: new Date(settings.updated_at),
        trend: 'stable'
      });
    }

    // Preferências de tema
    if (settings.theme === 'dark') {
      patterns.push({
        type: 'preference',
        pattern: 'dark_theme_preference',
        confidence: 1.0,
        evidence: [settings],
        lastObserved: new Date(settings.updated_at),
        trend: 'stable'
      });
    }

    return patterns;
  }

  private assessCurrentState(context: SATIContext, patterns: UserPattern[]): ContextualInsights['currentState'] {
    const now = new Date();
    const hour = now.getHours();

    // Verificar se está em horário de pico
    const peakHourPattern = patterns.find(p => p.pattern.startsWith('peak_hours_'));
    if (peakHourPattern) {
      const peakHours = peakHourPattern.pattern.split('_').slice(2).map(h => parseInt(h));
      if (peakHours.includes(hour)) {
        return 'energetic';
      }
    }

    // Verificar última sessão
    if (context.recentSessions && context.recentSessions.length > 0) {
      const lastSession = context.recentSessions[0];
      const timeSinceLastSession = Date.now() - new Date(lastSession.ended_at || lastSession.started_at).getTime();
      
      if (timeSinceLastSession < 300000) { // 5 minutos
        return lastSession.completed ? 'focused' : 'distracted';
      }
      
      if (timeSinceLastSession > 3600000) { // 1 hora
        return 'neutral';
      }
    }

    // Estado baseado no horário
    if (hour < 9 || hour > 20) return 'tired';
    if (hour >= 9 && hour <= 11) return 'energetic';
    if (hour >= 14 && hour <= 16) return 'focused';
    
    return 'neutral';
  }

  private suggestOptimalAction(
    state: ContextualInsights['currentState'],
    context: SATIContext,
    patterns: UserPattern[]
  ): string {
    switch (state) {
      case 'energetic':
        return 'Aproveite sua energia alta para tarefas complexas';
      case 'focused':
        return 'Continue com foco nas tarefas atuais';
      case 'distracted':
        return 'Faça uma pausa breve ou mude para tarefa mais simples';
      case 'tired':
        return 'Considere uma pausa mais longa ou tarefas administrativas';
      default:
        return 'Comece com uma tarefa de aquecimento';
    }
  }

  private identifyRiskFactors(context: SATIContext, patterns: UserPattern[]): string[] {
    const risks: string[] = [];

    // Verificar padrão de alta interrupção
    const interruptionPattern = patterns.find(p => p.pattern === 'high_interruption_frequency');
    if (interruptionPattern) {
      risks.push('Alta frequência de interrupções detectada');
    }

    // Verificar tendência de declínio
    const decliningPatterns = patterns.filter(p => p.trend === 'declining');
    if (decliningPatterns.length > 0) {
      risks.push('Tendência de declínio na produtividade');
    }

    // Verificar horário não ótimo
    const now = new Date().getHours();
    const peakPattern = patterns.find(p => p.pattern.startsWith('peak_hours_'));
    if (peakPattern) {
      const peakHours = peakPattern.pattern.split('_').slice(2).map(h => parseInt(h));
      if (!peakHours.includes(now)) {
        risks.push('Horário fora do seu pico de produtividade');
      }
    }

    return risks;
  }

  private identifyOpportunities(context: SATIContext, patterns: UserPattern[]): string[] {
    const opportunities: string[] = [];

    // Verificar padrões de melhoria
    const improvingPatterns = patterns.filter(p => p.trend === 'improving');
    if (improvingPatterns.length > 0) {
      opportunities.push('Tendência positiva de melhoria detectada');
    }

    // Verificar horário ótimo
    const now = new Date().getHours();
    const peakPattern = patterns.find(p => p.pattern.startsWith('peak_hours_'));
    if (peakPattern) {
      const peakHours = peakPattern.pattern.split('_').slice(2).map(h => parseInt(h));
      if (peakHours.includes(now)) {
        opportunities.push('Você está no seu horário de pico de produtividade');
      }
    }

    // Verificar sessões consecutivas bem-sucedidas
    if (context.recentSessions) {
      const recentCompleted = context.recentSessions
        .filter(s => s.completed && new Date(s.started_at) > new Date(Date.now() - 2 * 60 * 60 * 1000))
        .length;
      
      if (recentCompleted >= 2) {
        opportunities.push('Sequência positiva de sessões completadas');
      }
    }

    return opportunities;
  }

  private generateRecommendations(
    state: ContextualInsights['currentState'],
    context: SATIContext,
    patterns: UserPattern[]
  ): string[] {
    const recommendations: string[] = [];

    // Recomendações baseadas no estado atual
    switch (state) {
      case 'energetic':
        recommendations.push('Tackle your most challenging task now');
        break;
      case 'tired':
        recommendations.push('Take a 10-minute break or switch to easier tasks');
        break;
      case 'distracted':
        recommendations.push('Try a 5-minute meditation or change your environment');
        break;
    }

    // Recomendações baseadas em padrões
    const optimalDurationPattern = patterns.find(p => p.pattern.includes('optimal_duration_'));
    if (optimalDurationPattern && context.userSettings) {
      const optimalMinutes = parseInt(optimalDurationPattern.pattern.split('_')[2].replace('min', ''));
      const currentMinutes = context.userSettings.focus_duration / 60;
      
      if (Math.abs(optimalMinutes - currentMinutes) > 5) {
        recommendations.push(`Consider adjusting session duration to ${optimalMinutes} minutes`);
      }
    }

    return recommendations;
  }

  // Métodos auxiliares para cálculos específicos
  private calculateHourlyProductivity(sessions: any[]): Record<string, number> {
    const hourly: Record<string, number[]> = {};
    
    sessions.forEach(session => {
      const hour = new Date(session.started_at).getHours().toString();
      const score = session.productivity_score || (session.completed ? 3 : 1);
      
      if (!hourly[hour]) hourly[hour] = [];
      hourly[hour].push(score);
    });

    const averages: Record<string, number> = {};
    Object.entries(hourly).forEach(([hour, scores]) => {
      averages[hour] = scores.reduce((a, b) => a + b, 0) / scores.length;
    });

    return averages;
  }

  private findOptimalSessionDuration(sessions: any[]): number {
    // Encontrar duração que resulta em maior taxa de conclusão
    const durationGroups: Record<number, { completed: number; total: number }> = {};
    
    sessions.forEach(session => {
      const duration = Math.round(session.duration / 300) * 300; // Agrupar em intervalos de 5 min
      
      if (!durationGroups[duration]) {
        durationGroups[duration] = { completed: 0, total: 0 };
      }
      
      durationGroups[duration].total++;
      if (session.completed) {
        durationGroups[duration].completed++;
      }
    });

    let bestDuration = 1500; // Padrão
    let bestRate = 0;
    
    Object.entries(durationGroups).forEach(([duration, stats]) => {
      const rate = stats.completed / stats.total;
      if (rate > bestRate && stats.total >= 3) { // Mínimo de 3 sessões para ser significativo
        bestRate = rate;
        bestDuration = parseInt(duration);
      }
    });

    return bestDuration;
  }

  private calculateTrend(sessions: any[], type: string): 'improving' | 'declining' | 'stable' {
    if (sessions.length < 10) return 'stable';

    const recent = sessions.slice(0, Math.floor(sessions.length / 2));
    const older = sessions.slice(Math.floor(sessions.length / 2));

    let recentScore = 0;
    let olderScore = 0;

    if (type === 'productivity') {
      recentScore = recent.reduce((acc, s) => acc + (s.productivity_score || (s.completed ? 3 : 1)), 0) / recent.length;
      olderScore = older.reduce((acc, s) => acc + (s.productivity_score || (s.completed ? 3 : 1)), 0) / older.length;
    }

    const diff = recentScore - olderScore;
    
    if (diff > 0.3) return 'improving';
    if (diff < -0.3) return 'declining';
    return 'stable';
  }

  private calculateConfidence(data: Record<string, number>, selectedItems: any[]): number {
    const values = Object.values(data);
    const selectedValues = selectedItems.map(item => data[item.toString()]);
    
    const avgSelected = selectedValues.reduce((a, b) => a + b, 0) / selectedValues.length;
    const avgAll = values.reduce((a, b) => a + b, 0) / values.length;
    
    return Math.min(0.95, 0.5 + (avgSelected - avgAll) / avgAll);
  }

  // Outros métodos auxiliares continuam...
  private getTimeContext() {
    const now = new Date();
    return {
      timeOfDay: this.getTimeOfDayCategory(now.getHours()),
      dayOfWeek: now.getDay().toString()
    };
  }

  private getTimeOfDayCategory(hour: number): string {
    if (hour < 6) return 'early_morning';
    if (hour < 12) return 'morning';
    if (hour < 18) return 'afternoon';
    if (hour < 22) return 'evening';
    return 'night';
  }
}
```

## Sistema de Métricas Avançadas

```typescript
// src/services/analyticsEngine.ts
export class AnalyticsEngine {
  async analyzeUserPatterns(userId: string, context: SATIContext): Promise<any> {
    const [
      productivityTrends,
      behaviorPatterns,
      performanceMetrics
    ] = await Promise.all([
      this.analyzeProductivityTrends(userId),
      this.analyzeBehaviorPatterns(userId),
      this.calculatePerformanceMetrics(userId)
    ]);

    return {
      productivityTrends,
      behaviorPatterns,
      performanceMetrics,
      insights: this.generateInsights(productivityTrends, behaviorPatterns, performanceMetrics)
    };
  }

  private async analyzeProductivityTrends(userId: string): Promise<any> {
    // Implementar análise de tendências de produtividade
    // Calcular métricas como:
    // - Taxa de conclusão de tarefas
    // - Tempo médio de foco
    // - Padrões de interrupção
    // - Eficiência por categoria de tarefa
  }

  private async analyzeBehaviorPatterns(userId: string): Promise<any> {
    // Implementar análise de padrões comportamentais
    // Identificar:
    // - Horários de maior produtividade
    // - Padrões de procrastinação
    // - Preferências de duração de sessão
    // - Fatores de distração
  }

  private calculatePerformanceMetrics(userId: string): Promise<any> {
    // Calcular métricas de performance
    // Incluir:
    // - Score de produtividade
    // - Consistência
    // - Melhoria ao longo do tempo
    // - Comparação com metas
  }

  private generateInsights(trends: any, patterns: any, metrics: any): any {
    // Gerar insights baseados nas análises
    // Combinar dados para identificar:
    // - Oportunidades de melhoria
    // - Pontos fortes
    // - Recomendações personalizadas
  }
}
```

## Interface de Insights

```typescript
// src/components/SATI/InsightsPanel.tsx
import React, { useEffect, useState } from 'react';
import { ContextManager, ContextualInsights } from '../../services/contextManager';

export function InsightsPanel({ userId }: { userId: string }) {
  const [insights, setInsights] = useState<ContextualInsights | null>(null);
  const [loading, setLoading] = useState(true);
  
  const contextManager = new ContextManager();

  useEffect(() => {
    loadInsights();
  }, [userId]);

  const loadInsights = async () => {
    try {
      setLoading(true);
      const context = await contextManager.buildContext(userId);
      const contextualInsights = await contextManager.generateContextualInsights(userId, context);
      setInsights(contextualInsights);
    } catch (error) {
      console.error('Erro ao carregar insights:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Carregando insights...</div>;
  if (!insights) return <div>Nenhum insight disponível</div>;

  return (
    <div className="insights-panel">
      <div className="current-state">
        <h3>Estado Atual</h3>
        <div className={`state-indicator ${insights.currentState}`}>
          {insights.currentState}
        </div>
      </div>

      <div className="optimal-action">
        <h3>Ação Recomendada</h3>
        <p>{insights.optimalNextAction}</p>
      </div>

      {insights.riskFactors.length > 0 && (
        <div className="risk-factors">
          <h3>Fatores de Risco</h3>
          <ul>
            {insights.riskFactors.map((risk, index) => (
              <li key={index} className="risk-item">{risk}</li>
            ))}
          </ul>
        </div>
      )}

      {insights.opportunities.length > 0 && (
        <div className="opportunities">
          <h3>Oportunidades</h3>
          <ul>
            {insights.opportunities.map((opportunity, index) => (
              <li key={index} className="opportunity-item">{opportunity}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="recommendations">
        <h3>Recomendações</h3>
        <ul>
          {insights.recommendations.map((rec, index) => (
            <li key={index} className="recommendation-item">{rec}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

## Testes de Análise de Contexto

```typescript
// src/tests/contextManager.test.ts
describe('Context Manager', () => {
  let contextManager: ContextManager;

  beforeEach(() => {
    contextManager = new ContextManager();
  });

  test('should identify peak productivity hours', async () => {
    const patterns = await contextManager.analyzeUserPatterns('test-user');
    const peakPattern = patterns.find(p => p.pattern.startsWith('peak_hours_'));
    
    expect(peakPattern).toBeDefined();
    expect(peakPattern?.confidence).toBeGreaterThan(0.7);
  });

  test('should assess current state correctly', async () => {
    const context = await contextManager.buildContext('test-user');
    const insights = await contextManager.generateContextualInsights('test-user', context);
    
    expect(['focused', 'distracted', 'tired', 'energetic', 'neutral']).toContain(insights.currentState);
  });

  test('should generate relevant recommendations', async () => {
    const context = await contextManager.buildContext('test-user');
    const insights = await contextManager.generateContextualInsights('test-user', context);
    
    expect(insights.recommendations.length).toBeGreaterThan(0);
    expect(insights.optimalNextAction).toBeDefined();
  });
});
```
