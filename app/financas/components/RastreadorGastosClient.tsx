'use client';

import dynamic from 'next/dynamic';

const RastreadorGastos = dynamic(
  () => import('@/app/components/financas/RastreadorGastos'),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-500 dark:text-gray-400">Carregando gráfico de gastos...</p>
        </div>
      </div>
    )
  }
);

export default function RastreadorGastosClient() {
  return <RastreadorGastos />;
}
