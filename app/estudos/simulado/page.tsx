'use client'; // Necessário para usar hooks como useState e useEffect, e o store Zustand

import React, { useState, Suspense, lazy } from 'react';
import { useSimuladoStore } from '@/app/stores/simuladoStore';
// Padronizando a forma de importação para todos os componentes
import SimuladoLoader from '@/app/components/estudos/simulado/SimuladoLoader';
import SimuladoReview from '@/app/components/estudos/simulado/SimuladoReview';
// Lazy loading para o componente que usa recharts
const SimuladoResults = lazy(() => import('@/app/components/estudos/simulado/SimuladoResults'));
import HistoricoModal from '@/app/components/estudos/simulado/HistoricoModal';
import { Container } from '@/app/components/ui/Container';
import { Button } from '@/app/components/ui/Button';
import { History } from 'lucide-react';

const SimuladoPage: React.FC = () => {
  const { status, resetSimulado } = useSimuladoStore();
  const [isHistoricoOpen, setIsHistoricoOpen] = useState(false); // <-- Estado para controlar o modal

  const renderContent = () => {
    switch (status) {
      case 'reviewing':
        return <SimuladoReview />;
      case 'results':
        return (
          <Suspense fallback={
            <div className="flex items-center justify-center p-8">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">Carregando resultados...</p>
              </div>
            </div>
          }>
            <SimuladoResults />
          </Suspense>
        );
      case 'loading': // Estado de loading visual melhorado
        return (
          <div className="flex items-center justify-center p-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400">Carregando simulado...</p>
            </div>
          </div>
        );
      case 'idle':
      default:
        return <SimuladoLoader />;
    }
  };

  return (
    <> {/* Usar Fragment para envolver Container e Modal */}
      <Container>
        <div className="flex justify-between items-center mb-6 gap-2"> {/* Adicionado gap */}
          <h1 className="text-2xl font-bold">Conferência de Simulado</h1>
          <div className="flex gap-2"> {/* Agrupar botões */}
            <Button onClick={() => setIsHistoricoOpen(true)} variant="outline" size="sm">
              <History className="mr-1 h-4 w-4" /> Histórico
            </Button>
            {status !== 'idle' && (
              <Button onClick={resetSimulado} variant="outline" size="sm">
                Carregar Novo
              </Button>
            )}
          </div>
        </div>
        {renderContent()}
      </Container>

      {/* Modal do Histórico */}
      <HistoricoModal
        isOpen={isHistoricoOpen}
        onClose={() => setIsHistoricoOpen(false)}
      />
    </>
  );
};

export default SimuladoPage;
