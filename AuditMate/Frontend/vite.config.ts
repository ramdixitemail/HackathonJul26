import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '')
  const configuredPort = env.VITE_API_PROXY_PORT?.trim()
  const apiProxyTarget =
    env.VITE_API_PROXY_TARGET ||
    (configuredPort ? `http://127.0.0.1:${configuredPort}` : 'http://127.0.0.1:8000')

  console.log(`[AuditMate] Proxying /api to ${apiProxyTarget}`)

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: apiProxyTarget,
          changeOrigin: true
        }
      }
    }
  }
})
