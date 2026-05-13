import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        // Use 127.0.0.1 (IPv4) instead of localhost
        // On modern Windows, localhost resolves to ::1 (IPv6) which
        // uvicorn doesn't listen on by default → ECONNREFUSED
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})

