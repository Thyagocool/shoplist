import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'favicon.svg', 'icons/*.png'],
      devOptions: {
        enabled: true,
      },
      manifest: {
        name: 'Shoplist',
        short_name: 'Shoplist',
        description: 'Sua lista de compras inteligente',
        theme_color: '#e31414',
        background_color: '#ffffff',
        display: 'standalone',
        scope: '/',
        start_url: '/',
        icons: [
          { src: '/icons/192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^\/api\/v1\/lists\/.*$/,
            handler: 'NetworkFirst',
            options: { cacheName: 'api-list-cache' },
          },
        ],
      },
    }),
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://api:8000',
        changeOrigin: true,
      },
      '/uploads': {
        target: 'http://api:8000',
        changeOrigin: true,
      },
    },
  },
});
