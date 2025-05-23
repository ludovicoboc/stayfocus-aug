# Configuração de Storage

## Contexto

O armazenamento de arquivos é um componente importante do StayFocus, permitindo que os usuários armazenem e acessem documentos, imagens e outros arquivos relacionados aos seus estudos, notas de autoconhecimento e outros módulos da aplicação. O Supabase Storage oferece uma solução robusta para armazenamento de arquivos, com controle de acesso granular através de políticas de segurança.

Além disso, conforme mencionado na documentação do projeto, há a necessidade de integração com o Google Drive para acesso a materiais de estudo, o que requer uma abordagem híbrida para gerenciamento de arquivos.

## Buckets de Armazenamento

No Supabase Storage, os arquivos são organizados em "buckets" (contêineres). Para o StayFocus, criaremos os seguintes buckets:

### 1. Bucket para Materiais de Estudo

```sql
-- Criar bucket para materiais de estudo
INSERT INTO storage.buckets (id, name, public)
VALUES (
  'materiais-estudo',
  'Materiais de Estudo',
  false
);

-- Configurar políticas de acesso
CREATE POLICY "Usuários podem visualizar seus próprios materiais de estudo"
ON storage.objects FOR SELECT
USING (
  auth.uid() = (storage.foldername(name))[1]::uuid
);

CREATE POLICY "Usuários podem fazer upload de seus próprios materiais de estudo"
ON storage.objects FOR INSERT
WITH CHECK (
  auth.uid() = (storage.foldername(name))[1]::uuid
);

CREATE POLICY "Usuários podem atualizar seus próprios materiais de estudo"
ON storage.objects FOR UPDATE
USING (
  auth.uid() = (storage.foldername(name))[1]::uuid
);

CREATE POLICY "Usuários podem excluir seus próprios materiais de estudo"
ON storage.objects FOR DELETE
USING (
  auth.uid() = (storage.foldername(name))[1]::uuid
);
```

### 2. Bucket para Imagens de Notas de Autoconhecimento

```sql
-- Criar bucket para imagens de notas de autoconhecimento
INSERT INTO storage.buckets (id, name, public)
VALUES (
  'autoconhecimento-imagens',
  'Imagens de Autoconhecimento',
  false
);

-- Configurar políticas de acesso
CREATE POLICY "Usuários podem visualizar suas próprias imagens de autoconhecimento"
ON storage.objects FOR SELECT
USING (
  auth.uid() = (storage.foldername(name))[1]::uuid
);

CREATE POLICY "Usuários podem fazer upload de suas próprias imagens de autoconhecimento"
ON storage.objects FOR INSERT
WITH CHECK (
  auth.uid() = (storage.foldername(name))[1]::uuid
);

CREATE POLICY "Usuários podem atualizar suas próprias imagens de autoconhecimento"
ON storage.objects FOR UPDATE
USING (
  auth.uid() = (storage.foldername(name))[1]::uuid
);

CREATE POLICY "Usuários podem excluir suas próprias imagens de autoconhecimento"
ON storage.objects FOR DELETE
USING (
  auth.uid() = (storage.foldername(name))[1]::uuid
);
```

### 3. Bucket para Editais de Concursos

```sql
-- Criar bucket para editais de concursos
INSERT INTO storage.buckets (id, name, public)
VALUES (
  'editais-concursos',
  'Editais de Concursos',
  false
);

-- Configurar políticas de acesso
CREATE POLICY "Usuários podem visualizar seus próprios editais de concursos"
ON storage.objects FOR SELECT
USING (
  auth.uid() = (storage.foldername(name))[1]::uuid
);

CREATE POLICY "Usuários podem fazer upload de seus próprios editais de concursos"
ON storage.objects FOR INSERT
WITH CHECK (
  auth.uid() = (storage.foldername(name))[1]::uuid
);

CREATE POLICY "Usuários podem atualizar seus próprios editais de concursos"
ON storage.objects FOR UPDATE
USING (
  auth.uid() = (storage.foldername(name))[1]::uuid
);

CREATE POLICY "Usuários podem excluir seus próprios editais de concursos"
ON storage.objects FOR DELETE
USING (
  auth.uid() = (storage.foldername(name))[1]::uuid
);
```

### 4. Bucket para Avatares de Usuários

```sql
-- Criar bucket para avatares de usuários
INSERT INTO storage.buckets (id, name, public)
VALUES (
  'avatares',
  'Avatares de Usuários',
  true
);

-- Configurar políticas de acesso
CREATE POLICY "Qualquer pessoa pode visualizar avatares"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'avatares'
);

CREATE POLICY "Usuários podem fazer upload de seus próprios avatares"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'avatares' AND
  auth.uid() = (storage.foldername(name))[1]::uuid
);

CREATE POLICY "Usuários podem atualizar seus próprios avatares"
ON storage.objects FOR UPDATE
USING (
  bucket_id = 'avatares' AND
  auth.uid() = (storage.foldername(name))[1]::uuid
);

CREATE POLICY "Usuários podem excluir seus próprios avatares"
ON storage.objects FOR DELETE
USING (
  bucket_id = 'avatares' AND
  auth.uid() = (storage.foldername(name))[1]::uuid
);
```

## Implementação no Frontend

### 1. Hooks para Gerenciamento de Arquivos

Crie um hook personalizado para gerenciar o upload, download e exclusão de arquivos:

```typescript
// app/hooks/useStorage.ts
import { useState } from 'react'
import { supabase } from '../lib/supabase/client'

export function useStorage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Upload de arquivo
  const uploadFile = async (
    bucketName: string,
    filePath: string,
    file: File,
    options?: { contentType?: string }
  ) => {
    try {
      setLoading(true)
      setError(null)

      const { data, error } = await supabase.storage
        .from(bucketName)
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: true,
          contentType: options?.contentType,
        })

      if (error) {
        throw error
      }

      return { data }
    } catch (err: any) {
      setError(err.message || 'Erro ao fazer upload do arquivo')
      return { error: err }
    } finally {
      setLoading(false)
    }
  }

  // Download de arquivo
  const downloadFile = async (bucketName: string, filePath: string) => {
    try {
      setLoading(true)
      setError(null)

      const { data, error } = await supabase.storage
        .from(bucketName)
        .download(filePath)

      if (error) {
        throw error
      }

      return { data }
    } catch (err: any) {
      setError(err.message || 'Erro ao baixar o arquivo')
      return { error: err }
    } finally {
      setLoading(false)
    }
  }

  // Exclusão de arquivo
  const deleteFile = async (bucketName: string, filePath: string) => {
    try {
      setLoading(true)
      setError(null)

      const { data, error } = await supabase.storage
        .from(bucketName)
        .remove([filePath])

      if (error) {
        throw error
      }

      return { data }
    } catch (err: any) {
      setError(err.message || 'Erro ao excluir o arquivo')
      return { error: err }
    } finally {
      setLoading(false)
    }
  }

  // Obter URL pública
  const getPublicUrl = (bucketName: string, filePath: string) => {
    const { data } = supabase.storage
      .from(bucketName)
      .getPublicUrl(filePath)

    return data.publicUrl
  }

  // Listar arquivos
  const listFiles = async (bucketName: string, folderPath?: string) => {
    try {
      setLoading(true)
      setError(null)

      const { data, error } = await supabase.storage
        .from(bucketName)
        .list(folderPath || '')

      if (error) {
        throw error
      }

      return { data }
    } catch (err: any) {
      setError(err.message || 'Erro ao listar arquivos')
      return { error: err }
    } finally {
      setLoading(false)
    }
  }

  return {
    loading,
    error,
    uploadFile,
    downloadFile,
    deleteFile,
    getPublicUrl,
    listFiles,
  }
}
```

### 2. Componente de Upload de Arquivo

```tsx
// app/components/common/FileUploader.tsx
import { useState } from 'react'
import { useStorage } from '../../hooks/useStorage'
import { useAuth } from '../../hooks/useAuth'

interface FileUploaderProps {
  bucketName: string
  folderPath?: string
  onUploadComplete?: (filePath: string, fileUrl: string) => void
  acceptedFileTypes?: string
  maxSizeMB?: number
}

export function FileUploader({
  bucketName,
  folderPath = '',
  onUploadComplete,
  acceptedFileTypes = '*',
  maxSizeMB = 10,
}: FileUploaderProps) {
  const [file, setFile] = useState<File | null>(null)
  const [progress, setProgress] = useState(0)
  const { uploadFile, getPublicUrl } = useStorage()
  const { user } = useAuth()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0]
      
      // Verificar tamanho do arquivo
      if (selectedFile.size > maxSizeMB * 1024 * 1024) {
        alert(`O arquivo é muito grande. O tamanho máximo é ${maxSizeMB}MB.`)
        return
      }
      
      setFile(selectedFile)
    }
  }

  const handleUpload = async () => {
    if (!file || !user) return
    
    // Criar caminho do arquivo incluindo ID do usuário
    const filePath = `${user.id}/${folderPath}/${Date.now()}_${file.name}`
    
    // Simular progresso (na verdade, o Supabase não fornece progresso de upload)
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 95) {
          clearInterval(interval)
          return 95
        }
        return prev + 5
      })
    }, 100)
    
    // Fazer upload do arquivo
    const { data, error } = await uploadFile(bucketName, filePath, file)
    
    clearInterval(interval)
    
    if (error) {
      setProgress(0)
      alert(`Erro ao fazer upload: ${error.message}`)
      return
    }
    
    setProgress(100)
    
    // Obter URL pública
    const fileUrl = getPublicUrl(bucketName, filePath)
    
    // Chamar callback
    if (onUploadComplete) {
      onUploadComplete(filePath, fileUrl)
    }
    
    // Resetar após upload
    setTimeout(() => {
      setFile(null)
      setProgress(0)
    }, 2000)
  }

  return (
    <div className="file-uploader">
      <input
        type="file"
        accept={acceptedFileTypes}
        onChange={handleFileChange}
        disabled={!user}
      />
      
      {file && (
        <div className="file-info">
          <p>{file.name} ({(file.size / 1024 / 1024).toFixed(2)}MB)</p>
          <button onClick={handleUpload}>Fazer Upload</button>
        </div>
      )}
      
      {progress > 0 && (
        <div className="progress-bar">
          <div className="progress" style={{ width: `${progress}%` }}></div>
          <span>{progress}%</span>
        </div>
      )}
    </div>
  )
}
```

## Integração com Google Drive

Conforme mencionado na documentação, o StayFocus requer integração com o Google Drive para acesso a materiais de estudo. Vamos implementar essa integração:

### 1. Tabela para Rastreamento de Arquivos do Google Drive

```sql
-- Tabela para rastrear arquivos do Google Drive
CREATE TABLE materiais_drive (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  tipo TEXT NOT NULL,
  folder_id TEXT NOT NULL,
  file_id TEXT,
  file_name TEXT,
  last_accessed TIMESTAMP WITH TIME ZONE DEFAULT now(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Habilitar RLS
ALTER TABLE materiais_drive ENABLE ROW LEVEL SECURITY;

-- Políticas de RLS
CREATE POLICY "Usuários podem ler apenas seus próprios materiais do Drive"
ON materiais_drive FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Usuários podem inserir apenas seus próprios materiais do Drive"
ON materiais_drive FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuários podem atualizar apenas seus próprios materiais do Drive"
ON materiais_drive FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Usuários podem excluir apenas seus próprios materiais do Drive"
ON materiais_drive FOR DELETE
USING (auth.uid() = user_id);
```

### 2. Integração com a API do Google Drive

A integração com o Google Drive já está parcialmente implementada no projeto através do arquivo `app/lib/googleDriveClient.ts`. Vamos estender essa implementação para armazenar referências aos arquivos no Supabase:

```typescript
// app/services/DriveService.ts
import { getAuthenticatedClient } from '../lib/googleDriveClient'
import { supabase } from '../lib/supabase/client'
import { IronSession } from 'iron-session'

export class DriveService {
  // Listar materiais do Drive
  static async listarMateriais(session: IronSession, tipo: string, folderId: string) {
    try {
      // Obter cliente autenticado do Google Drive
      const driveClient = await getAuthenticatedClient(session)
      if (!driveClient) {
        throw new Error('Não foi possível autenticar com o Google Drive')
      }
      
      // Obter arquivos da pasta
      const drive = google.drive({ version: 'v3', auth: driveClient })
      const response = await drive.files.list({
        q: `'${folderId}' in parents and trashed = false`,
        fields: 'files(id, name, mimeType, webViewLink, iconLink)',
      })
      
      const files = response.data.files || []
      
      // Armazenar referências no Supabase
      const userId = session.user?.id
      if (userId) {
        for (const file of files) {
          // Verificar se o arquivo já está registrado
          const { data: existingFile } = await supabase
            .from('materiais_drive')
            .select('*')
            .eq('user_id', userId)
            .eq('file_id', file.id)
            .single()
          
          if (!existingFile) {
            // Registrar novo arquivo
            await supabase.from('materiais_drive').insert({
              user_id: userId,
              tipo,
              folder_id: folderId,
              file_id: file.id,
              file_name: file.name,
            })
          } else {
            // Atualizar último acesso
            await supabase
              .from('materiais_drive')
              .update({ last_accessed: new Date().toISOString() })
              .eq('id', existingFile.id)
          }
        }
      }
      
      return files
    } catch (error) {
      console.error('Erro ao listar materiais do Drive:', error)
      throw error
    }
  }
}
```

## Próximos Passos

Após a configuração do Storage, os próximos passos são:

1. Implementar a integração com o frontend para upload e download de arquivos
2. Desenvolver as Edge Functions necessárias
3. Implementar a sincronização em tempo real
4. Configurar backups automáticos para os dados armazenados

A configuração adequada do Storage é essencial para garantir que os usuários possam armazenar e acessar seus arquivos de forma segura e eficiente, seja através do Supabase Storage ou do Google Drive.
