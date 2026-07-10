import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * ── SECURITY WARNING ──
 * The dev server proxies below point DIRECTLY to the Materna FastAPI (:8000),
 * bypassing Clinify's JWT + doctor-role auth layer. This is INTENTIONAL for
 * standalone UI development (e.g., working on the Materna SPA without Clinify).
 *
 * In production, Vercel serves this standalone reference UI. Clinify links to
 * it through VITE_MATERNA_EXTERNAL_URL.
 *
 * DO NOT expose this dev server to any network. It is for localhost only.
 */
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    allowedHosts: ["localhost", "192.168.18.183", ".ngrok.io", ".ngrok-free.app"],
    // Dev-only proxies — bypass Clinify auth. NOT for production use.
    proxy: {
      '/health': 'http://localhost:8000',
      '/cases': 'http://localhost:8000',
      '/extract': 'http://localhost:8000',
      '/extract-image': 'http://localhost:8000',
      '/demo': 'http://localhost:8000',
    },
  },
})
