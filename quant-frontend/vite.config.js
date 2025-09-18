import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/backtest': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/stocks': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/strategy': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    },
    // 允许从任何主机访问
    host: '0.0.0.0'
  }
})
