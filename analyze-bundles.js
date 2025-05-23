/**
 * Script para analisar os bundles e identificar oportunidades de otimização
 * 
 * Este script é executado após a análise de bundle e fornece recomendações
 * para melhorar o desempenho da aplicação.
 */

const fs = require('fs');
const path = require('path');

// Caminho para o relatório do bundle analyzer
const REPORT_PATH = path.join(__dirname, '.next', 'analyze', 'client.html');

// Limites para alertas
const SIZE_THRESHOLDS = {
  LARGE: 100 * 1024, // 100KB
  MEDIUM: 50 * 1024,  // 50KB
  SMALL: 20 * 1024    // 20KB
};

// Bibliotecas que podem ser carregadas de forma assíncrona
const ASYNC_LOAD_CANDIDATES = [
  'recharts',
  'date-fns',
  'lucide-react',
  '@headlessui/react',
  'zustand',
  'iron-session',
  'googleapis',
];

// Bibliotecas que podem ser substituídas por alternativas mais leves
const REPLACEABLE_LIBRARIES = {
  'moment': 'date-fns',
  'lodash': 'lodash-es (importações específicas)',
  'jquery': 'vanilla JS ou pequenas utilidades',
  'axios': 'fetch API',
};

/**
 * Verifica se o relatório do bundle analyzer existe
 */
function checkReportExists() {
  if (!fs.existsSync(REPORT_PATH)) {
    console.error('\x1b[31m%s\x1b[0m', 'Erro: Relatório do bundle analyzer não encontrado.');
    console.log('Execute primeiro: npm run analyze');
    process.exit(1);
  }
}

/**
 * Analisa o HTML do relatório para extrair informações sobre os bundles
 */
function parseReport() {
  try {
    const html = fs.readFileSync(REPORT_PATH, 'utf8');
    
    // Extrai dados do script que contém as informações do bundle
    const dataMatch = html.match(/var chartData = (\[.*?\]);/s);
    if (!dataMatch || !dataMatch[1]) {
      throw new Error('Não foi possível extrair os dados do bundle do relatório');
    }
    
    // Converte a string JSON para objeto JavaScript
    // Nota: Isso é uma simplificação, em um caso real seria necessário um parser mais robusto
    const bundleData = JSON.parse(dataMatch[1].replace(/'/g, '"'));
    
    return bundleData;
  } catch (error) {
    console.error('\x1b[31m%s\x1b[0m', `Erro ao analisar o relatório: ${error.message}`);
    process.exit(1);
  }
}

/**
 * Identifica bibliotecas grandes que podem ser carregadas de forma assíncrona
 */
function identifyLargeLibraries(bundleData) {
  const largeLibraries = [];
  
  // Função recursiva para percorrer a árvore de módulos
  function traverseModules(modules) {
    modules.forEach(module => {
      // Verifica se é uma biblioteca e se é grande o suficiente para ser considerada
      if (module.path && module.path.includes('node_modules') && module.statSize > SIZE_THRESHOLDS.MEDIUM) {
        // Extrai o nome da biblioteca do caminho
        const libraryMatch = module.path.match(/node_modules[/\\]([^/\\]+)(?:[/\\]|$)/);
        if (libraryMatch && libraryMatch[1]) {
          const libraryName = libraryMatch[1].startsWith('@') 
            ? `${libraryMatch[1]}/${module.path.split(libraryMatch[1] + '/')[1].split('/')[0]}`
            : libraryMatch[1];
          
          largeLibraries.push({
            name: libraryName,
            size: module.statSize,
            path: module.path
          });
        }
      }
      
      // Continua a busca recursivamente
      if (module.groups && module.groups.length > 0) {
        traverseModules(module.groups);
      }
    });
  }
  
  traverseModules(bundleData);
  
  // Remove duplicatas e ordena por tamanho
  const uniqueLibraries = Array.from(
    new Map(largeLibraries.map(lib => [lib.name, lib])).values()
  ).sort((a, b) => b.size - a.size);
  
  return uniqueLibraries;
}

/**
 * Gera recomendações com base nas bibliotecas identificadas
 */
function generateRecommendations(largeLibraries) {
  const recommendations = {
    asyncLoading: [],
    codeImports: [],
    replacements: []
  };
  
  largeLibraries.forEach(lib => {
    // Recomenda carregamento assíncrono para bibliotecas candidatas
    if (ASYNC_LOAD_CANDIDATES.some(candidate => lib.name.includes(candidate))) {
      recommendations.asyncLoading.push(lib);
    }
    
    // Recomenda importações específicas para bibliotecas grandes
    if (lib.size > SIZE_THRESHOLDS.LARGE) {
      recommendations.codeImports.push(lib);
    }
    
    // Recomenda substituições para bibliotecas que têm alternativas mais leves
    Object.keys(REPLACEABLE_LIBRARIES).forEach(replaceableLib => {
      if (lib.name.includes(replaceableLib)) {
        recommendations.replacements.push({
          current: lib,
          alternative: REPLACEABLE_LIBRARIES[replaceableLib]
        });
      }
    });
  });
  
  return recommendations;
}

/**
 * Exibe as recomendações no console
 */
function displayRecommendations(recommendations, largeLibraries) {
  console.log('\n\x1b[36m%s\x1b[0m', '📊 ANÁLISE DE BUNDLES - STAYFOCUS');
  console.log('\x1b[36m%s\x1b[0m', '=====================================');
  
  // Exibe as maiores bibliotecas
  console.log('\n\x1b[33m%s\x1b[0m', '🔍 MAIORES BIBLIOTECAS:');
  largeLibraries.slice(0, 10).forEach((lib, index) => {
    const sizeInKB = (lib.size / 1024).toFixed(2);
    console.log(`${index + 1}. ${lib.name}: ${sizeInKB} KB`);
  });
  
  // Exibe recomendações para carregamento assíncrono
  if (recommendations.asyncLoading.length > 0) {
    console.log('\n\x1b[32m%s\x1b[0m', '⚡ RECOMENDAÇÕES PARA LAZY LOADING:');
    recommendations.asyncLoading.forEach((lib, index) => {
      const sizeInKB = (lib.size / 1024).toFixed(2);
      console.log(`${index + 1}. ${lib.name} (${sizeInKB} KB)`);
      console.log(`   Use: import dynamic from 'next/dynamic'`);
      console.log(`   const ${lib.name.replace(/[-/@]/g, '_')} = dynamic(() => import('${lib.name}'), { ssr: false })`);
    });
  }
  
  // Exibe recomendações para importações específicas
  if (recommendations.codeImports.length > 0) {
    console.log('\n\x1b[32m%s\x1b[0m', '📦 RECOMENDAÇÕES PARA IMPORTAÇÕES ESPECÍFICAS:');
    recommendations.codeImports.forEach((lib, index) => {
      const sizeInKB = (lib.size / 1024).toFixed(2);
      console.log(`${index + 1}. ${lib.name} (${sizeInKB} KB)`);
      console.log(`   Ao invés de: import { everything } from '${lib.name}'`);
      console.log(`   Use: import { apenasOQueVocêPrecisa } from '${lib.name}'`);
    });
  }
  
  // Exibe recomendações para substituições
  if (recommendations.replacements.length > 0) {
    console.log('\n\x1b[32m%s\x1b[0m', '🔄 RECOMENDAÇÕES PARA SUBSTITUIÇÕES:');
    recommendations.replacements.forEach((item, index) => {
      const sizeInKB = (item.current.size / 1024).toFixed(2);
      console.log(`${index + 1}. Substitua ${item.current.name} (${sizeInKB} KB) por ${item.alternative}`);
    });
  }
  
  console.log('\n\x1b[36m%s\x1b[0m', '📝 PRÓXIMOS PASSOS:');
  console.log('1. Implemente lazy loading para componentes que usam bibliotecas pesadas');
  console.log('2. Otimize importações para incluir apenas o necessário');
  console.log('3. Configure corretamente o tree-shaking no webpack');
  console.log('4. Considere usar o Turbopack para desenvolvimento mais rápido');
  console.log('\n\x1b[36m%s\x1b[0m', '=====================================');
}

/**
 * Função principal
 */
function main() {
  try {
    checkReportExists();
    const bundleData = parseReport();
    const largeLibraries = identifyLargeLibraries(bundleData);
    const recommendations = generateRecommendations(largeLibraries);
    displayRecommendations(recommendations, largeLibraries);
  } catch (error) {
    console.error('\x1b[31m%s\x1b[0m', `Erro inesperado: ${error.message}`);
    process.exit(1);
  }
}

// Executa o script
main();
