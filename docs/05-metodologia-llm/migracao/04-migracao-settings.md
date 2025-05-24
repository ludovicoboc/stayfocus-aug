# Migração Settings Store

## Objetivo
Migrar as configurações do usuário do localStorage para Supabase, mantendo preferências e personalizações.

## Pré-requisitos
- ✅ Configuração inicial do Supabase completa
- ✅ Schema da tabela `user_settings` criado
- ✅ RLS configurado
- ✅ Backup do localStorage realizado

## Estrutura da Tabela Settings

```sql
CREATE TABLE user_settings (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  
  -- Configurações Pomodoro
  focus_duration INTEGER DEFAULT 1500, -- 25 minutos em segundos
  short_break_duration INTEGER DEFAULT 300, -- 5 minutos
  long_break_duration INTEGER DEFAULT 900, -- 15 minutos
  sessions_until_long_break INTEGER DEFAULT 4,
  auto_start_breaks BOOLEAN DEFAULT false,
  auto_start_focus BOOLEAN DEFAULT false,
  
  -- Configurações de Interface
  theme VARCHAR(20) DEFAULT 'light', -- 'light', 'dark', 'auto'
  language VARCHAR(10) DEFAULT 'pt-BR',
  sound_enabled BOOLEAN DEFAULT true,
  notification_enabled BOOLEAN DEFAULT true,
  
  -- Configurações de Produtividade
  daily_goal_sessions INTEGER DEFAULT 8,
  show_productivity_tips BOOLEAN DEFAULT true,
  enable_website_blocking BOOLEAN DEFAULT false,
  blocked_websites TEXT[],
  
  -- Configurações Avançadas
  data_retention_days INTEGER DEFAULT 365,
  sync_enabled BOOLEAN DEFAULT true,
  backup_frequency VARCHAR(20) DEFAULT 'daily', -- 'daily', 'weekly', 'monthly'
  
  -- Metadados
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Configurações SATI
  sati_enabled BOOLEAN DEFAULT true,
  sati_voice_mode BOOLEAN DEFAULT false,
  sati_proactive_suggestions BOOLEAN DEFAULT true,
  sati_learning_mode BOOLEAN DEFAULT true
);

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_user_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_settings_updated_at
  BEFORE UPDATE ON user_settings
  FOR EACH ROW
  EXECUTE FUNCTION update_user_settings_updated_at();
```

## Etapas de Migração

### 1. Análise dos Dados Existentes
```typescript
// Verificar configurações atuais
const currentSettings = localStorage.getItem('stayfocus_settings');
const settingsData = JSON.parse(currentSettings || '{}');

console.log('Configurações atuais:', settingsData);

// Mapear configurações para nova estrutura
const defaultSettings = {
  focus_duration: 1500,
  short_break_duration: 300,
  long_break_duration: 900,
  sessions_until_long_break: 4,
  theme: 'light',
  language: 'pt-BR',
  sound_enabled: true,
  notification_enabled: true,
  daily_goal_sessions: 8
};

// Identificar configurações customizadas
const customizedSettings = {};
Object.keys(settingsData).forEach(key => {
  if (settingsData[key] !== defaultSettings[key]) {
    customizedSettings[key] = settingsData[key];
  }
});

console.log('Configurações customizadas:', customizedSettings);
```

### 2. Criação do Service de Settings
```typescript
// src/services/settingsService.ts
import { supabase } from './supabaseClient';

export interface UserSettings {
  id?: string;
  user_id?: string;
  focus_duration?: number;
  short_break_duration?: number;
  long_break_duration?: number;
  sessions_until_long_break?: number;
  auto_start_breaks?: boolean;
  auto_start_focus?: boolean;
  theme?: 'light' | 'dark' | 'auto';
  language?: string;
  sound_enabled?: boolean;
  notification_enabled?: boolean;
  daily_goal_sessions?: number;
  show_productivity_tips?: boolean;
  enable_website_blocking?: boolean;
  blocked_websites?: string[];
  data_retention_days?: number;
  sync_enabled?: boolean;
  backup_frequency?: 'daily' | 'weekly' | 'monthly';
  sati_enabled?: boolean;
  sati_voice_mode?: boolean;
  sati_proactive_suggestions?: boolean;
  sati_learning_mode?: boolean;
}

export class SettingsService {
  async getUserSettings(userId: string): Promise<UserSettings> {
    const { data, error } = await supabase
      .from('user_settings')
      .select('*')
      .eq('user_id', userId)
      .single();
    
    if (error && error.code !== 'PGRST116') { // Not found
      throw error;
    }
    
    // Se não existir, criar configurações padrão
    if (!data) {
      return this.createDefaultSettings(userId);
    }
    
    return data;
  }

  async createDefaultSettings(userId: string): Promise<UserSettings> {
    const defaultSettings: Partial<UserSettings> = {
      user_id: userId,
      focus_duration: 1500,
      short_break_duration: 300,
      long_break_duration: 900,
      sessions_until_long_break: 4,
      auto_start_breaks: false,
      auto_start_focus: false,
      theme: 'light',
      language: 'pt-BR',
      sound_enabled: true,
      notification_enabled: true,
      daily_goal_sessions: 8,
      show_productivity_tips: true,
      enable_website_blocking: false,
      blocked_websites: [],
      data_retention_days: 365,
      sync_enabled: true,
      backup_frequency: 'daily',
      sati_enabled: true,
      sati_voice_mode: false,
      sati_proactive_suggestions: true,
      sati_learning_mode: true
    };

    const { data, error } = await supabase
      .from('user_settings')
      .insert([defaultSettings])
      .select()
      .single();
    
    if (error) throw error;
    return data;
  }

  async updateSettings(userId: string, updates: Partial<UserSettings>): Promise<UserSettings> {
    // Remover campos que não devem ser atualizados
    const { id, user_id, created_at, updated_at, ...cleanUpdates } = updates;

    const { data, error } = await supabase
      .from('user_settings')
      .update(cleanUpdates)
      .eq('user_id', userId)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  }

  async resetToDefaults(userId: string): Promise<UserSettings> {
    // Deletar configurações atuais
    await supabase
      .from('user_settings')
      .delete()
      .eq('user_id', userId);
    
    // Criar novas configurações padrão
    return this.createDefaultSettings(userId);
  }

  async exportSettings(userId: string): Promise<UserSettings> {
    const settings = await this.getUserSettings(userId);
    
    // Remover dados internos
    const { id, user_id, created_at, updated_at, ...exportableSettings } = settings;
    
    return exportableSettings;
  }

  async importSettings(userId: string, settings: Partial<UserSettings>): Promise<UserSettings> {
    // Validar configurações importadas
    const validatedSettings = this.validateSettings(settings);
    
    return this.updateSettings(userId, validatedSettings);
  }

  private validateSettings(settings: Partial<UserSettings>): Partial<UserSettings> {
    const validated: Partial<UserSettings> = {};

    // Validar durações (mínimo 1 minuto, máximo 120 minutos)
    if (settings.focus_duration) {
      validated.focus_duration = Math.max(60, Math.min(7200, settings.focus_duration));
    }
    
    if (settings.short_break_duration) {
      validated.short_break_duration = Math.max(60, Math.min(1800, settings.short_break_duration));
    }
    
    if (settings.long_break_duration) {
      validated.long_break_duration = Math.max(300, Math.min(3600, settings.long_break_duration));
    }

    // Validar tema
    if (settings.theme && ['light', 'dark', 'auto'].includes(settings.theme)) {
      validated.theme = settings.theme;
    }

    // Validar idioma
    if (settings.language) {
      validated.language = settings.language;
    }

    // Copiar configurações booleanas
    const booleanFields = [
      'auto_start_breaks', 'auto_start_focus', 'sound_enabled', 
      'notification_enabled', 'show_productivity_tips', 'enable_website_blocking',
      'sync_enabled', 'sati_enabled', 'sati_voice_mode', 
      'sati_proactive_suggestions', 'sati_learning_mode'
    ];

    booleanFields.forEach(field => {
      if (typeof settings[field] === 'boolean') {
        validated[field] = settings[field];
      }
    });

    // Validar arrays
    if (Array.isArray(settings.blocked_websites)) {
      validated.blocked_websites = settings.blocked_websites.filter(url => 
        typeof url === 'string' && url.length > 0
      );
    }

    return validated;
  }
}
```

### 3. Migração dos Dados
```typescript
async function migrateSettings() {
  try {
    const userId = await getCurrentUserId();
    const settingsService = new SettingsService();

    // 1. Ler configurações do localStorage
    const localSettings = JSON.parse(localStorage.getItem('stayfocus_settings') || '{}');
    console.log('Configurações locais:', localSettings);

    // 2. Mapear configurações para nova estrutura
    const mappedSettings: Partial<UserSettings> = {};

    // Mapear configurações Pomodoro
    if (localSettings.focusDuration) {
      mappedSettings.focus_duration = localSettings.focusDuration * 60; // minutos para segundos
    }
    if (localSettings.shortBreakDuration) {
      mappedSettings.short_break_duration = localSettings.shortBreakDuration * 60;
    }
    if (localSettings.longBreakDuration) {
      mappedSettings.long_break_duration = localSettings.longBreakDuration * 60;
    }
    if (localSettings.sessionsUntilLongBreak) {
      mappedSettings.sessions_until_long_break = localSettings.sessionsUntilLongBreak;
    }

    // Mapear configurações de interface
    if (localSettings.theme) {
      mappedSettings.theme = localSettings.theme;
    }
    if (localSettings.language) {
      mappedSettings.language = localSettings.language;
    }
    if (typeof localSettings.soundEnabled === 'boolean') {
      mappedSettings.sound_enabled = localSettings.soundEnabled;
    }
    if (typeof localSettings.notificationsEnabled === 'boolean') {
      mappedSettings.notification_enabled = localSettings.notificationsEnabled;
    }

    // Mapear outras configurações
    if (localSettings.dailyGoal) {
      mappedSettings.daily_goal_sessions = localSettings.dailyGoal;
    }
    if (Array.isArray(localSettings.blockedWebsites)) {
      mappedSettings.blocked_websites = localSettings.blockedWebsites;
    }

    // 3. Criar ou atualizar configurações
    let currentSettings;
    try {
      currentSettings = await settingsService.getUserSettings(userId);
    } catch (error) {
      // Se não existir, será criado com padrões
      currentSettings = await settingsService.createDefaultSettings(userId);
    }

    // 4. Aplicar configurações migradas
    if (Object.keys(mappedSettings).length > 0) {
      const updatedSettings = await settingsService.updateSettings(userId, mappedSettings);
      console.log('✅ Configurações migradas:', updatedSettings);
    } else {
      console.log('✅ Configurações padrão mantidas');
    }

    return currentSettings;
  } catch (error) {
    console.error('❌ Erro na migração de configurações:', error);
    throw error;
  }
}
```

### 4. Atualização dos Hooks
```typescript
// src/hooks/useSettings.ts
import { useState, useEffect } from 'react';
import { SettingsService, UserSettings } from '../services/settingsService';

export function useSettings() {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  const settingsService = new SettingsService();

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const userId = await getCurrentUserId();
      const userSettings = await settingsService.getUserSettings(userId);
      setSettings(userSettings);
    } catch (error) {
      console.error('Erro ao carregar configurações:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateSetting = async (key: keyof UserSettings, value: any) => {
    try {
      setSaving(true);
      const userId = await getCurrentUserId();
      const updatedSettings = await settingsService.updateSettings(userId, {
        [key]: value
      });
      setSettings(updatedSettings);
    } catch (error) {
      console.error('Erro ao atualizar configuração:', error);
      throw error;
    } finally {
      setSaving(false);
    }
  };

  const updateMultipleSettings = async (updates: Partial<UserSettings>) => {
    try {
      setSaving(true);
      const userId = await getCurrentUserId();
      const updatedSettings = await settingsService.updateSettings(userId, updates);
      setSettings(updatedSettings);
    } catch (error) {
      console.error('Erro ao atualizar configurações:', error);
      throw error;
    } finally {
      setSaving(false);
    }
  };

  const resetToDefaults = async () => {
    try {
      setSaving(true);
      const userId = await getCurrentUserId();
      const defaultSettings = await settingsService.resetToDefaults(userId);
      setSettings(defaultSettings);
    } catch (error) {
      console.error('Erro ao resetar configurações:', error);
      throw error;
    } finally {
      setSaving(false);
    }
  };

  const exportSettings = async () => {
    try {
      const userId = await getCurrentUserId();
      return await settingsService.exportSettings(userId);
    } catch (error) {
      console.error('Erro ao exportar configurações:', error);
      throw error;
    }
  };

  const importSettings = async (settingsData: Partial<UserSettings>) => {
    try {
      setSaving(true);
      const userId = await getCurrentUserId();
      const importedSettings = await settingsService.importSettings(userId, settingsData);
      setSettings(importedSettings);
    } catch (error) {
      console.error('Erro ao importar configurações:', error);
      throw error;
    } finally {
      setSaving(false);
    }
  };

  return {
    settings,
    loading,
    saving,
    updateSetting,
    updateMultipleSettings,
    resetToDefaults,
    exportSettings,
    importSettings,
    refreshSettings: loadSettings
  };
}
```

### 5. Context Provider para Settings
```typescript
// src/contexts/SettingsContext.tsx
import React, { createContext, useContext, ReactNode } from 'react';
import { useSettings } from '../hooks/useSettings';

const SettingsContext = createContext(null);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const settingsData = useSettings();
  
  return (
    <SettingsContext.Provider value={settingsData}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettingsContext() {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettingsContext deve ser usado dentro de SettingsProvider');
  }
  return context;
}
```

## Validação e Testes

### 1. Validação de Migração
```typescript
async function validateSettingsMigration() {
  const localSettings = JSON.parse(localStorage.getItem('stayfocus_settings') || '{}');
  const userId = await getCurrentUserId();
  const settingsService = new SettingsService();
  const supabaseSettings = await settingsService.getUserSettings(userId);

  console.log('Configurações locais:', localSettings);
  console.log('Configurações migradas:', supabaseSettings);

  // Verificar campos críticos
  const criticalFields = ['focus_duration', 'theme', 'sound_enabled'];
  
  for (const field of criticalFields) {
    if (supabaseSettings[field] === undefined) {
      throw new Error(`Campo crítico ausente: ${field}`);
    }
  }

  console.log('✅ Validação de configurações bem-sucedida');
}
```

### 2. Teste de Sincronização
```typescript
async function testSettingsSync() {
  const settingsService = new SettingsService();
  const userId = await getCurrentUserId();

  // Teste de atualização
  const originalSettings = await settingsService.getUserSettings(userId);
  
  await settingsService.updateSettings(userId, {
    theme: 'dark',
    sound_enabled: false
  });

  const updatedSettings = await settingsService.getUserSettings(userId);
  
  if (updatedSettings.theme !== 'dark' || updatedSettings.sound_enabled !== false) {
    throw new Error('Falha na sincronização de configurações');
  }

  console.log('✅ Teste de sincronização bem-sucedido');
}
```

## Checklist de Validação
- [ ] Configurações migradas corretamente
- [ ] Configurações padrão aplicadas
- [ ] Validação de dados funcionando
- [ ] Sincronização em tempo real
- [ ] Export/Import funcionando
- [ ] Reset para padrões funcional
- [ ] Context Provider configurado
- [ ] Backup local mantido
