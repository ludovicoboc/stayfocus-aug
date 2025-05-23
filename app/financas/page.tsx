import { Suspense, lazy } from 'react'
import dynamic from 'next/dynamic'
import { Card } from '@/app/components/ui/Card'
import { EnvelopesVirtuais } from '@/app/components/financas/EnvelopesVirtuais'
import { CalendarioPagamentos } from '@/app/components/financas/CalendarioPagamentos'
import { AdicionarDespesa } from '@/app/components/financas/AdicionarDespesa'

// Importação dinâmica otimizada para o RastreadorGastos
// Usando dynamic do Next.js com configurações para melhor performance
const RastreadorGastos = dynamic(
  () => import('@/app/components/financas/RastreadorGastos'),
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

export default function FinancasPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Finanças</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Rastreador de Gastos */}
        <Card title="Rastreador de Gastos">
          <RastreadorGastos />
        </Card>

        {/* Envelopes Virtuais */}
        <Card title="Envelopes Virtuais">
          <EnvelopesVirtuais />
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Calendário de Pagamentos */}
        <Card title="Calendário de Pagamentos">
          <CalendarioPagamentos />
        </Card>

        {/* Adicionar Despesa Rápida */}
        <Card title="Adicionar Despesa">
          <AdicionarDespesa />
        </Card>
      </div>
    </div>
  )
}
