'use client'

import { Suspense, lazy } from 'react'
import dynamic from 'next/dynamic'
import { RegistroMedicamentos } from '@/app/components/saude/RegistroMedicamentos'

// Importação dinâmica para o wrapper do componente MonitoramentoHumor
const MonitoramentoHumor = dynamic(
  () => import('@/app/components/saude/MonitoramentoHumorWrapper'),
  {
    ssr: false, // Desabilita SSR pois pode depender de APIs do browser
    loading: () => (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 animate-pulse">
        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-6"></div>
        <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mx-auto"></div>
      </div>
    )
  }
)

export default function SaudePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Saúde</h1>

      <div className="grid grid-cols-1 gap-6">
        {/* Registro de Medicamentos */}
        <RegistroMedicamentos />

        {/* Monitoramento de Humor com lazy loading */}
        <MonitoramentoHumor />
      </div>
    </div>
  )
}
