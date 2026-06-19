import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    allowedHosts: ["localhost", "192.168.18.183", ".ngrok.io", ".ngrok-free.app"],
    proxy: {
      '/health': 'http://localhost:8000',
      '/cases': 'http://localhost:8000',
      '/extract': 'http://localhost:8000',
      '/extract-image': 'http://localhost:8000',
      '/demo': 'http://localhost:8000',
    },
  },
})
