'use client'

import { Suspense } from 'react'
import dynamic from 'next/dynamic'
import { Card } from '@/app/components/ui/Card'

// Importação dinâmica otimizada para o RastreadorGastos
const RastreadorGastos = dynamic(
  () => import('@/app/components/financas/RastreadorGastos').then(mod => mod.default),
  {
    ssr: false, // Desabilita SSR pois recharts depende de APIs do browser
    loading: () => (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-500 dark:text-gray-400">Carregando gráfico de gastos...</p>
        </div>
      </div>
    )
  }
)

export function RastreadorGastosClient() {
  return (
    <Card title="Rastreador de Gastos">
      <Suspense fallback={
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary mx-auto"></div>
        </div>
      }>
        <RastreadorGastos />
      </Suspense>
    </Card>
  )
}
