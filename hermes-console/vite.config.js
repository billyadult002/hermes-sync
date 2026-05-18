import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    historyApiFallback: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8765',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return undefined
          if (id.includes('react')) return 'react-vendor'
          if (id.includes('react-router')) return 'router'
          if (id.includes('recharts') || id.includes('d3-')) return 'charts'
          if (id.includes('socket.io-client')) return 'socket'
          if (id.includes('@chakra-ui')) return 'chakra'
          if (id.includes('@emotion') || id.includes('framer-motion')) return 'emotion'
          if (id.includes('@zag-js') || id.includes('@ark-ui') || id.includes('@pandacss')) return 'ui-foundation'
          if (id.includes('axios')) return 'http'
          return 'vendor'
        },
      },
    },
  },
})
