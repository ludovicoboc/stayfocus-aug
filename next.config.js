const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
  // Configurações adicionais para o bundle analyzer
  openAnalyzer: true,
  analyzerMode: 'server',
  analyzerPort: 8888,
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Configuração para usar o Turbopack em desenvolvimento
  experimental: {
    // Habilitar o Turbopack para desenvolvimento mais rápido
    turbo: {
      // Configurações do Turbopack
      resolveAlias: {
        // Aliases para melhorar a resolução de módulos
        '@': '.',
      },
    },
    // Otimizações para melhorar o desempenho
    optimizePackageImports: [
      'react',
      'react-dom',
      'lucide-react',
      'recharts',
      'date-fns',
      '@headlessui/react',
      'zustand'
    ],
    // Habilitar o code-splitting automático
    optimizeCss: true,
    // Melhorar o carregamento de fontes
    fontLoaders: [
      { loader: '@next/font/google', options: { subsets: ['latin'] } },
    ],
  },
  // Configuração para otimizar imagens
  images: {
    domains: [],
    formats: ['image/avif', 'image/webp'],
  },
}

module.exports = withBundleAnalyzer(nextConfig)
