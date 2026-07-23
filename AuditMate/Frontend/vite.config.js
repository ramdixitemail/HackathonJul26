import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig(function (_a) {
    var _b;
    var mode = _a.mode;
    var env = loadEnv(mode, '.', '');
    var configuredPort = (_b = env.VITE_API_PROXY_PORT) === null || _b === void 0 ? void 0 : _b.trim();
    var apiProxyTarget = env.VITE_API_PROXY_TARGET ||
        (configuredPort ? "http://127.0.0.1:".concat(configuredPort) : 'http://127.0.0.1:8000');
    console.log("[AuditMate] Proxying /api to ".concat(apiProxyTarget));
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
    };
});
