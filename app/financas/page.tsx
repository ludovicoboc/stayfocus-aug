import { Card } from '@/app/components/ui/Card'
import { EnvelopesVirtuais } from '@/app/components/financas/EnvelopesVirtuais'
import { CalendarioPagamentos } from '@/app/components/financas/CalendarioPagamentos'
import { AdicionarDespesa } from '@/app/components/financas/AdicionarDespesa'
import RastreadorGastosClient from './components/RastreadorGastosClient'

export default function FinancasPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Finanças</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Rastreador de Gastos */}
        <Card title="Rastreador de Gastos">
          <RastreadorGastosClient />
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
