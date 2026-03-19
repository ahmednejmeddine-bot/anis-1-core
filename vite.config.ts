import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const BACKEND = 'http://localhost:8000'

const PROXY_RULES = {
  '/api':              { target: BACKEND, changeOrigin: true },
  '/health':           { target: BACKEND, changeOrigin: true },
  '/agents':           { target: BACKEND, changeOrigin: true },
  '/dispatch_task':    { target: BACKEND, changeOrigin: true },
  '/executive_status': { target: BACKEND, changeOrigin: true },
}

export default defineConfig({
  plugins: [react()],

  // Development server (npm run dev)
  server: {
    host: '0.0.0.0',
    port: 5000,
    allowedHosts: true,
    proxy: PROXY_RULES,
  },

  // Production preview server (npm run preview — used by start.sh)
  preview: {
    host: '0.0.0.0',
    port: 5000,
    allowedHosts: true,
    proxy: PROXY_RULES,
  },
})
